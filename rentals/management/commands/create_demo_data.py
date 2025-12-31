"""
Django management command to create dummy data for testing.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rentals.models import Book, Rental
from rentals.services import OpenLibraryService


class Command(BaseCommand):
    help = 'Create dummy data for testing the book rental system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Rental.objects.all().delete()
            Book.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('✓ Data cleared'))

        self.stdout.write(self.style.SUCCESS('\n📚 Creating Book Rental System Demo Data...\n'))

        # Create student users
        students_data = [
            {
                'username': 'john_doe',
                'email': 'john.doe@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'password': 'student123'
            },
            {
                'username': 'jane_smith',
                'email': 'jane.smith@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'password': 'student123'
            },
            {
                'username': 'bob_wilson',
                'email': 'bob.wilson@example.com',
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'password': 'student123'
            },
            {
                'username': 'alice_brown',
                'email': 'alice.brown@example.com',
                'first_name': 'Alice',
                'last_name': 'Brown',
                'password': 'student123'
            },
            {
                'username': 'charlie_davis',
                'email': 'charlie.davis@example.com',
                'first_name': 'Charlie',
                'last_name': 'Davis',
                'password': 'student123'
            },
        ]

        students = []
        self.stdout.write('\n👥 Creating students...')
        for student_data in students_data:
            user, created = User.objects.get_or_create(
                username=student_data['username'],
                defaults={
                    'email': student_data['email'],
                    'first_name': student_data['first_name'],
                    'last_name': student_data['last_name'],
                }
            )
            if created:
                user.set_password(student_data['password'])
                user.save()
                self.stdout.write(f'  ✓ Created: {user.get_full_name()} ({user.username})')
            else:
                self.stdout.write(f'  → Exists: {user.get_full_name()} ({user.username})')
            students.append(user)

        # Popular books to fetch from OpenLibrary
        book_titles = [
            "Harry Potter and the Philosopher's Stone",
            "The Great Gatsby",
            "To Kill a Mockingbird",
            "1984",
            "Pride and Prejudice",
            "The Catcher in the Rye",
            "The Hobbit",
            "Animal Farm",
        ]

        books = []
        self.stdout.write('\n📖 Fetching books from OpenLibrary API...')
        for title in book_titles:
            # Try to get existing book first
            existing_book = Book.objects.filter(title__icontains=title.split()[0]).first()
            if existing_book:
                books.append(existing_book)
                self.stdout.write(f'  → Exists: {existing_book.title} ({existing_book.number_of_pages} pages)')
                continue

            self.stdout.write(f'  🔍 Searching: {title}...')
            book_data = OpenLibraryService.search_book_by_title(title)
            
            if book_data:
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
                books.append(book)
                monthly_fee = book.monthly_rental_fee()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ {book.title} by {book.author} '
                        f'({book.number_of_pages} pages, ${monthly_fee:.2f}/month)'
                    )
                )
            else:
                self.stdout.write(self.style.WARNING(f'  ✗ Could not fetch: {title}'))

        if not books:
            self.stdout.write(self.style.ERROR('\n✗ No books found. Cannot create rentals.'))
            return

        # Create rentals with various scenarios
        self.stdout.write('\n📋 Creating rentals...')
        
        rental_scenarios = [
            # John Doe - Active rentals, some extended
            {
                'student': students[0],
                'book': books[0] if len(books) > 0 else None,
                'days_ago': 10,
                'extensions': 0,
                'status': 'active',
                'description': 'Active rental, still in free month'
            },
            {
                'student': students[0],
                'book': books[1] if len(books) > 1 else None,
                'days_ago': 35,
                'extensions': 1,
                'status': 'active',
                'description': 'Extended once, has charges'
            },
            
            # Jane Smith - Mix of active and returned
            {
                'student': students[1],
                'book': books[2] if len(books) > 2 else None,
                'days_ago': 5,
                'extensions': 0,
                'status': 'active',
                'description': 'Recently rented'
            },
            {
                'student': students[1],
                'book': books[3] if len(books) > 3 else None,
                'days_ago': 45,
                'extensions': 2,
                'status': 'returned',
                'description': 'Returned after 2 extensions'
            },
            
            # Bob Wilson - Multiple extensions
            {
                'student': students[2],
                'book': books[4] if len(books) > 4 else None,
                'days_ago': 90,
                'extensions': 3,
                'status': 'active',
                'description': 'Long-term rental with 3 extensions'
            },
            
            # Alice Brown - Recent rental
            {
                'student': students[3],
                'book': books[5] if len(books) > 5 else None,
                'days_ago': 2,
                'extensions': 0,
                'status': 'active',
                'description': 'Brand new rental'
            },
            {
                'student': students[3],
                'book': books[6] if len(books) > 6 else None,
                'days_ago': 60,
                'extensions': 1,
                'status': 'returned',
                'description': 'Returned with charges'
            },
            
            # Charlie Davis - Overdue scenario
            {
                'student': students[4],
                'book': books[7] if len(books) > 7 else None,
                'days_ago': 40,
                'extensions': 0,
                'status': 'active',
                'description': 'Overdue (past due date)'
            },
        ]

        created_rentals = []
        for scenario in rental_scenarios:
            if not scenario['book']:
                continue
                
            # Create rental with backdated rental_date
            rental_date = timezone.now() - timedelta(days=scenario['days_ago'])
            rental = Rental.objects.create(
                user=scenario['student'],
                book=scenario['book'],
                rental_date=rental_date,
                status=scenario['status']
            )
            
            # Set due date based on rental date
            rental.due_date = rental_date + timedelta(days=30)
            
            # Apply extensions
            if scenario['extensions'] > 0:
                for _ in range(scenario['extensions']):
                    rental.months_extended += 1
                    rental.due_date += timedelta(days=30)
                rental.calculate_charges()
            
            # Set return date for returned rentals
            if scenario['status'] == 'returned':
                rental.return_date = timezone.now() - timedelta(days=1)
            
            rental.save()
            created_rentals.append(rental)
            
            status_emoji = '✓' if scenario['status'] == 'active' else '↩'
            charge_info = f'${rental.total_charges:.2f}' if rental.total_charges > 0 else 'FREE'
            
            self.stdout.write(
                f'  {status_emoji} {scenario["student"].get_full_name()}: '
                f'{scenario["book"].title} '
                f'[{scenario["status"].upper()}, {charge_info}]'
            )
            self.stdout.write(f'     → {scenario["description"]}')

        # Summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('\n✅ Demo Data Creation Complete!\n'))
        self.stdout.write(f'👥 Students created: {len(students)}')
        self.stdout.write(f'📚 Books fetched: {len(books)}')
        self.stdout.write(f'📋 Rentals created: {len(created_rentals)}')
        
        # Calculate statistics
        active_rentals = sum(1 for r in created_rentals if r.status == 'active')
        returned_rentals = sum(1 for r in created_rentals if r.status == 'returned')
        from decimal import Decimal
        total_charges = sum((Decimal(str(r.total_charges)) for r in created_rentals), Decimal('0'))
        
        self.stdout.write(f'   - Active: {active_rentals}')
        self.stdout.write(f'   - Returned: {returned_rentals}')
        self.stdout.write(f'💰 Total charges: ${total_charges:.2f}')
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write('\n🚀 Next Steps:')
        self.stdout.write('  1. Start server: python manage.py runserver')
        self.stdout.write('  2. Go to: http://127.0.0.1:8000/admin/')
        self.stdout.write('  3. Login: admin / admin123')
        self.stdout.write('  4. Explore:')
        self.stdout.write('     - View Rentals list')
        self.stdout.write('     - Check Student Dashboard')
        self.stdout.write('     - Try extending rentals')
        self.stdout.write('     - Create new rentals')
        self.stdout.write('\n📝 Student accounts (all password: student123):')
        for student in students:
            self.stdout.write(f'     - {student.username}')
        self.stdout.write('')
