"""
Django management command to quickly create dummy data without API calls.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rentals.models import Book, Rental


class Command(BaseCommand):
    help = 'Quickly create dummy data without API calls'

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

        self.stdout.write(self.style.SUCCESS('\n📚 Creating Demo Data (Fast Mode)...\n'))

        # Create student users
        students_data = [
            ('john_doe', 'John', 'Doe', 'john.doe@example.com'),
            ('jane_smith', 'Jane', 'Smith', 'jane.smith@example.com'),
            ('bob_wilson', 'Bob', 'Wilson', 'bob.wilson@example.com'),
            ('alice_brown', 'Alice', 'Brown', 'alice.brown@example.com'),
            ('charlie_davis', 'Charlie', 'Davis', 'charlie.davis@example.com'),
        ]

        students = []
        self.stdout.write('👥 Creating students...')
        for username, first_name, last_name, email in students_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )
            if created:
                user.set_password('student123')
                user.save()
                self.stdout.write(f'  ✓ {user.get_full_name()} ({username})')
            else:
                self.stdout.write(f'  → {user.get_full_name()} (exists)')
            students.append(user)

        # Create books with realistic data
        books_data = [
            ("Harry Potter and the Philosopher's Stone", 'J.K. Rowling', 223),
            ('The Great Gatsby', 'F. Scott Fitzgerald', 180),
            ('To Kill a Mockingbird', 'Harper Lee', 324),
            ('1984', 'George Orwell', 328),
            ('Pride and Prejudice', 'Jane Austen', 279),
            ('The Catcher in the Rye', 'J.D. Salinger', 234),
            ('The Hobbit', 'J.R.R. Tolkien', 310),
            ('Animal Farm', 'George Orwell', 112),
            ('Lord of the Flies', 'William Golding', 224),
            ('The Lord of the Rings', 'J.R.R. Tolkien', 1178),
        ]

        books = []
        self.stdout.write('\n📖 Creating books...')
        for title, author, pages in books_data:
            book, created = Book.objects.get_or_create(
                title=title,
                defaults={
                    'author': author,
                    'number_of_pages': pages,
                }
            )
            books.append(book)
            fee = book.monthly_rental_fee()
            status = '✓' if created else '→'
            self.stdout.write(f'  {status} {title} by {author} ({pages} pages, ${fee:.2f}/mo)')

        # Create diverse rental scenarios
        self.stdout.write('\n📋 Creating rentals...')
        
        scenarios = [
            # (student_idx, book_idx, days_ago, extensions, status, description)
            (0, 0, 5, 0, 'active', 'John: Recent rental in free period'),
            (0, 1, 35, 1, 'active', 'John: Extended once, has charges'),
            (0, 2, 60, 2, 'returned', 'John: Returned after 2 extensions'),
            
            (1, 3, 10, 0, 'active', 'Jane: Active in free month'),
            (1, 4, 40, 1, 'returned', 'Jane: Returned with charges'),
            (1, 5, 70, 3, 'active', 'Jane: Long-term rental'),
            
            (2, 6, 2, 0, 'active', 'Bob: Just rented'),
            (2, 7, 90, 2, 'returned', 'Bob: Completed rental'),
            
            (3, 8, 15, 0, 'active', 'Alice: Mid-free-period'),
            (3, 9, 45, 1, 'active', 'Alice: Extended once'),
            
            (4, 0, 38, 0, 'active', 'Charlie: Overdue (past 30 days)'),
            (4, 1, 25, 0, 'active', 'Charlie: About to be due'),
        ]

        for student_idx, book_idx, days_ago, extensions, status, desc in scenarios:
            student = students[student_idx]
            book = books[book_idx]
            
            rental_date = timezone.now() - timedelta(days=days_ago)
            rental = Rental.objects.create(
                user=student,
                book=book,
                rental_date=rental_date,
                status=status
            )
            
            rental.due_date = rental_date + timedelta(days=30)
            
            if extensions > 0:
                for _ in range(extensions):
                    rental.months_extended += 1
                    rental.due_date += timedelta(days=30)
                rental.calculate_charges()
            
            if status == 'returned':
                rental.return_date = timezone.now() - timedelta(days=2)
            
            rental.save()
            
            emoji = '✓' if status == 'active' else '↩'
            charge = f'${rental.total_charges:.2f}' if rental.total_charges > 0 else 'FREE'
            self.stdout.write(f'  {emoji} {desc} [{charge}]')

        # Statistics
        total_rentals = Rental.objects.count()
        active = Rental.objects.filter(status='active').count()
        returned = Rental.objects.filter(status='returned').count()
        total_charges = sum(r.total_charges for r in Rental.objects.all())

        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('\n✅ Demo Data Created Successfully!\n'))
        self.stdout.write(f'👥 Students: {len(students)}')
        self.stdout.write(f'📚 Books: {len(books)}')
        self.stdout.write(f'📋 Rentals: {total_rentals}')
        self.stdout.write(f'   • Active: {active}')
        self.stdout.write(f'   • Returned: {returned}')
        self.stdout.write(f'💰 Total charges: ${total_charges:.2f}')
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('\n🚀 Ready to Test!\n'))
        self.stdout.write('1. Start server:')
        self.stdout.write('   python manage.py runserver\n')
        self.stdout.write('2. Open browser:')
        self.stdout.write('   http://127.0.0.1:8000/admin/\n')
        self.stdout.write('3. Login credentials:')
        self.stdout.write('   Username: admin')
        self.stdout.write('   Password: admin123\n')
        self.stdout.write('4. Test features:')
        self.stdout.write('   • View Rentals → See all rentals with statuses')
        self.stdout.write('   • Student Dashboard → Overview of all students')
        self.stdout.write('   • Create New Rental → Try adding a new book')
        self.stdout.write('   • Extend Rental → Select and extend active rentals')
        self.stdout.write('   • Books → View all available books\n')
        self.stdout.write('📝 Student login (password: student123):')
        for s in students:
            self.stdout.write(f'   • {s.username}')
        self.stdout.write('')
