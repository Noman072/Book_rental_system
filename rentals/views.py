from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from .models import Book, Rental
from .services import OpenLibraryService
from .forms import NewRentalForm, ExtendRentalForm


def is_admin(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Main admin dashboard."""
    total_books = Book.objects.count()
    total_students = User.objects.filter(is_staff=False, is_superuser=False).count()
    active_rentals = Rental.objects.filter(status='active').count()
    total_rentals = Rental.objects.count()
    
    recent_rentals = Rental.objects.select_related('user', 'book').order_by('-rental_date')[:10]
    
    context = {
        'total_books': total_books,
        'total_students': total_students,
        'active_rentals': active_rentals,
        'total_rentals': total_rentals,
        'recent_rentals': recent_rentals,
    }
    return render(request, 'rentals/admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def rental_list(request):
    """List all rentals."""
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    rentals = Rental.objects.select_related('user', 'book').order_by('-rental_date')
    
    if status_filter:
        rentals = rentals.filter(status=status_filter)
    
    if search:
        rentals = rentals.filter(
            Q(user__username__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(book__title__icontains=search)
        )
    
    context = {
        'rentals': rentals,
        'status_filter': status_filter,
        'search': search,
    }
    return render(request, 'rentals/admin/rental_list.html', context)


@login_required
@user_passes_test(is_admin)
def new_rental(request):
    """Create a new rental."""
    students = User.objects.filter(is_staff=False, is_superuser=False)
    
    if request.method == 'POST':
        user_id = request.POST.get('user')
        book_data_json = request.POST.get('book_data')
        
        if not user_id or not book_data_json:
            messages.error(request, 'Please select a student and choose a book from search results.')
            return redirect('new_rental')
        
        user = get_object_or_404(User, id=user_id)
        
        # Parse book data from JSON
        import json
        book_data = json.loads(book_data_json)
        
        # Create or get book
        book, created = Book.objects.get_or_create(
            title=book_data['title'],
            defaults={
                'author': book_data.get('author'),
                'isbn': book_data.get('isbn'),
                'number_of_pages': book_data.get('number_of_pages', 0),
                'cover_image_url': book_data.get('cover_image_url'),
                'openlibrary_key': book_data.get('openlibrary_key'),
            }
        )
        
        # Create rental
        rental = Rental.objects.create(user=user, book=book)
        
        messages.success(
            request,
            f'Rental created! {user.get_full_name() or user.username} can keep "{book.title}" '
            f'({book.number_of_pages} pages) for 1 month free. '
            f'Subsequent months: ${book.monthly_rental_fee():.2f}/month'
        )
        return redirect('rental_list')
    
    context = {'students': students}
    return render(request, 'rentals/admin/new_rental.html', context)


@login_required
@user_passes_test(is_admin)
def search_book_ajax(request):
    """AJAX endpoint for book search."""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 3:
        return JsonResponse({
            'success': False,
            'error': 'Please enter at least 3 characters'
        })
    
    try:
        # Fetch from OpenLibrary API
        book_data = OpenLibraryService.search_book_by_title(query)
        
        if book_data:
            return JsonResponse({
                'success': True,
                'book': {
                    'title': book_data['title'],
                    'author': book_data.get('author', 'Unknown Author'),
                    'number_of_pages': book_data.get('number_of_pages', 0),
                    'isbn': book_data.get('isbn'),
                    'cover_image_url': book_data.get('cover_image_url'),
                    'openlibrary_key': book_data.get('openlibrary_key'),
                    'monthly_fee': float(book_data.get('number_of_pages', 0)) / 100,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': f'No results found for "{query}"'
            })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error searching: {str(e)}'
        })


@login_required
@user_passes_test(is_admin)
def extend_rental(request, rental_id):
    """Extend a rental."""
    rental = get_object_or_404(Rental, id=rental_id)
    
    if request.method == 'POST':
        months = int(request.POST.get('months', 1))
        charges = rental.extend_rental(months=months)
        
        messages.success(
            request,
            f'Rental extended by {months} month(s). Additional charge: ${charges:.2f}'
        )
        return redirect('rental_list')
    
    context = {'rental': rental}
    return render(request, 'rentals/admin/extend_rental.html', context)


@login_required
@user_passes_test(is_admin)
def student_dashboard(request):
    """Dashboard showing all students and their rentals."""
    students = User.objects.filter(is_staff=False, is_superuser=False).distinct()
    
    student_data = []
    for student in students:
        rentals = Rental.objects.filter(user=student)
        total_rentals = rentals.count()
        active_rentals = rentals.filter(status='active').count()
        total_charges = rentals.aggregate(Sum('total_charges'))['total_charges__sum'] or 0
        
        student_data.append({
            'student': student,
            'total_rentals': total_rentals,
            'active_rentals': active_rentals,
            'total_charges': total_charges,
            'rentals': rentals.order_by('-rental_date')[:5]
        })
    
    context = {'student_data': student_data}
    return render(request, 'rentals/admin/student_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def book_list(request):
    """List all books."""
    search = request.GET.get('search', '')
    
    books = Book.objects.all().order_by('title')
    
    if search:
        books = books.filter(
            Q(title__icontains=search) | Q(author__icontains=search)
        )
    
    context = {
        'books': books,
        'search': search,
    }
    return render(request, 'rentals/admin/book_list.html', context)


@login_required
@user_passes_test(is_admin)
def mark_returned(request, rental_id):
    """Mark a rental as returned."""
    rental = get_object_or_404(Rental, id=rental_id)
    
    if rental.status == 'active':
        rental.status = 'returned'
        rental.return_date = timezone.now()
        rental.save()
        messages.success(request, f'Marked "{rental.book.title}" as returned.')
    else:
        messages.warning(request, 'This rental is not active.')
    
    return redirect('rental_list')


@login_required
@user_passes_test(is_admin)
def bulk_extend(request):
    """Bulk extend selected rentals."""
    if request.method == 'POST':
        rental_ids = request.POST.getlist('rental_ids')
        months = int(request.POST.get('months', 1))
        
        count = 0
        for rental_id in rental_ids:
            rental = Rental.objects.filter(id=rental_id, status='active').first()
            if rental:
                rental.extend_rental(months=months)
                count += 1
        
        messages.success(request, f'{count} rental(s) extended by {months} month(s).')
    
    return redirect('rental_list')
