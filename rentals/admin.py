from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count
from .models import Book, Rental
from .services import OpenLibraryService
from .forms import NewRentalForm, ExtendRentalForm


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Admin interface for Book model.
    """
    list_display = ['title', 'author', 'number_of_pages', 'monthly_fee_display', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'author', 'isbn']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'isbn', 'number_of_pages')
        }),
        ('Additional Details', {
            'fields': ('cover_image_url', 'openlibrary_key')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def monthly_fee_display(self, obj):
        """Display monthly rental fee."""
        return f"${obj.monthly_rental_fee():.2f}"
    monthly_fee_display.short_description = 'Monthly Fee'


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    """
    Admin interface for Rental model with custom actions and dashboard.
    """
    list_display = [
        'rental_id_display', 
        'user', 
        'book', 
        'rental_date', 
        'due_date', 
        'status_display',
        'months_extended',
        'charges_display',
        'days_remaining_display'
    ]
    list_filter = ['status', 'rental_date', 'due_date']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'book__title']
    readonly_fields = ['rental_date', 'total_charges', 'created_at', 'updated_at']
    actions = ['extend_rental_by_one_month', 'mark_as_returned']
    
    fieldsets = (
        ('Rental Information', {
            'fields': ('user', 'book', 'status')
        }),
        ('Dates', {
            'fields': ('rental_date', 'due_date', 'return_date')
        }),
        ('Charges', {
            'fields': ('months_extended', 'total_charges')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rental_id_display(self, obj):
        """Display rental ID."""
        return f"#{obj.id}"
    rental_id_display.short_description = 'Rental ID'
    
    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            'active': 'green',
            'returned': 'gray',
            'overdue': 'red'
        }
        status = obj.status
        if obj.is_overdue() and status == 'active':
            status = 'overdue'
        color = colors.get(status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            status.upper()
        )
    status_display.short_description = 'Status'
    
    def charges_display(self, obj):
        """Display total charges."""
        return f"${obj.total_charges:.2f}"
    charges_display.short_description = 'Total Charges'
    
    def days_remaining_display(self, obj):
        """Display days remaining."""
        if obj.status == 'returned':
            return 'Returned'
        days = obj.days_remaining()
        if days == 0 and obj.is_overdue():
            return format_html('<span style="color: red;">OVERDUE</span>')
        return f"{days} days"
    days_remaining_display.short_description = 'Days Remaining'
    
    def extend_rental_by_one_month(self, request, queryset):
        """Action to extend selected rentals by one month."""
        count = 0
        for rental in queryset:
            if rental.status != 'returned':
                rental.extend_rental(months=1)
                count += 1
        self.message_user(
            request, 
            f"{count} rental(s) extended by 1 month. Charges have been calculated.",
            messages.SUCCESS
        )
    extend_rental_by_one_month.short_description = "Extend selected rentals by 1 month"
    
    def mark_as_returned(self, request, queryset):
        """Action to mark selected rentals as returned."""
        from django.utils import timezone
        count = queryset.filter(status='active').update(
            status='returned',
            return_date=timezone.now()
        )
        self.message_user(
            request,
            f"{count} rental(s) marked as returned.",
            messages.SUCCESS
        )
    mark_as_returned.short_description = "Mark selected rentals as returned"
    
    def get_urls(self):
        """Add custom URLs for new rental and student dashboard."""
        urls = super().get_urls()
        custom_urls = [
            path('new-rental/', self.admin_site.admin_view(self.new_rental_view), name='rentals_new_rental'),
            path('student-dashboard/', self.admin_site.admin_view(self.student_dashboard_view), name='rentals_student_dashboard'),
            path('extend-rental/<int:rental_id>/', self.admin_site.admin_view(self.extend_rental_view), name='rentals_extend_rental'),
        ]
        return custom_urls + urls
    
    def new_rental_view(self, request):
        """View to create a new rental with OpenLibrary integration."""
        if request.method == 'POST':
            form = NewRentalForm(request.POST)
            if form.is_valid():
                user = form.cleaned_data['user']
                book_title = form.cleaned_data['book_title']
                
                # Fetch book from OpenLibrary
                book_data = OpenLibraryService.search_book_by_title(book_title)
                
                if book_data:
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
                    rental = Rental.objects.create(
                        user=user,
                        book=book
                    )
                    
                    messages.success(
                        request,
                        f"Rental created successfully! {user.username} can keep '{book.title}' "
                        f"({book.number_of_pages} pages) for 1 month free. "
                        f"Subsequent months: ${book.monthly_rental_fee():.2f}/month"
                    )
                    return redirect('admin:rentals_rental_changelist')
                else:
                    messages.error(request, f"Book '{book_title}' not found in OpenLibrary. Please try a different title.")
        else:
            form = NewRentalForm()
        
        context = {
            'title': 'Create New Rental',
            'form': form,
            'opts': self.model._meta,
            'has_view_permission': True,
        }
        return render(request, 'admin/rentals/new_rental.html', context)
    
    def extend_rental_view(self, request, rental_id):
        """View to extend an existing rental."""
        rental = get_object_or_404(Rental, id=rental_id)
        
        if request.method == 'POST':
            form = ExtendRentalForm(request.POST)
            if form.is_valid():
                months = form.cleaned_data['months']
                charges = rental.extend_rental(months=months)
                
                messages.success(
                    request,
                    f"Rental extended by {months} month(s). Additional charge: ${charges:.2f}"
                )
                return redirect('admin:rentals_rental_changelist')
        else:
            form = ExtendRentalForm()
        
        context = {
            'title': f'Extend Rental #{rental.id}',
            'form': form,
            'rental': rental,
            'opts': self.model._meta,
            'has_view_permission': True,
        }
        return render(request, 'admin/rentals/extend_rental.html', context)
    
    def student_dashboard_view(self, request):
        """Dashboard showing all rentals and fees for each student."""
        # Get all users who have rentals
        students = User.objects.filter(rentals__isnull=False).distinct()
        
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
                'rentals': rentals[:5]  # Show last 5 rentals
            })
        
        context = {
            'title': 'Student Rental Dashboard',
            'student_data': student_data,
            'opts': self.model._meta,
            'has_view_permission': True,
        }
        return render(request, 'admin/rentals/student_dashboard.html', context)


# Customize the admin site
admin.site.site_header = "Book Rental System Administration"
admin.site.site_title = "Book Rental Admin"
admin.site.index_title = "Welcome to Book Rental System"
