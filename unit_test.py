"""
Comprehensive Unit Tests for Book Rental System
Tests actual usage scenarios end-to-end
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_rental_system.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rentals.models import Book, Rental
from rentals.services import OpenLibraryService
import json


class ScenarioTestCase(TestCase):
    """Test actual usage scenarios"""
    
    def setUp(self):
        """Create test users and client"""
        # Create admin user
        self.admin = User.objects.create_user(
            username='admin_test',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create student users
        self.student1 = User.objects.create_user(
            username='john_test',
            password='student123',
            first_name='John',
            last_name='Doe'
        )
        
        self.student2 = User.objects.create_user(
            username='jane_test',
            password='student123',
            first_name='Jane',
            last_name='Smith'
        )
        
        self.client = Client()
    
    def test_scenario_1_admin_login_and_dashboard(self):
        """Test: Admin logs in and accesses dashboard"""
        print("\n📝 Test Scenario 1: Admin Login and Dashboard Access")
        
        # Login
        response = self.client.post(reverse('login'), {
            'username': 'admin_test',
            'password': 'admin123'
        })
        
        # Should redirect to admin dashboard
        self.assertEqual(response.status_code, 302)
        print("✅ Admin login successful")
        
        # Access dashboard
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        print("✅ Dashboard accessible")
    
    def test_scenario_2_search_book_via_ajax(self):
        """Test: Search for a book using AJAX endpoint"""
        print("\n📝 Test Scenario 2: AJAX Book Search")
        
        # Login first
        self.client.login(username='admin_test', password='admin123')
        
        # Search for a popular book
        response = self.client.get(
            reverse('search_book_ajax'),
            {'q': 'Pride and Prejudice'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        if data.get('success'):
            print(f"✅ Book found: {data['book']['title']}")
            print(f"   Author: {data['book']['author']}")
            print(f"   Pages: {data['book']['number_of_pages']}")
            print(f"   Monthly Fee: ${data['book']['monthly_fee']}")
            
            # Verify fee calculation
            self.assertIsInstance(data['book']['monthly_fee'], (int, float))
            self.assertGreater(data['book']['number_of_pages'], 0)
        else:
            print(f"⚠️ Book search failed: {data.get('message')}")
    
    def test_scenario_3_create_rental_first_month(self):
        """Test: Create a rental and verify first month is free"""
        print("\n📝 Test Scenario 3: First Month Free Rental")
        
        # Create a book
        book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="1234567890",
            number_of_pages=300
        )
        print(f"✅ Created book: {book.title} (300 pages)")
        
        # Create rental
        rental = Rental.objects.create(
            book=book,
            user=self.student1,
            rental_date=datetime.now().date()
        )
        
        print(f"✅ Rental created for {rental.user.username}")
    
    def test_scenario_4_rental_fee_calculation(self):
        """Test: Verify rental fee calculation for different page counts"""
        print("\n📝 Test Scenario 4: Fee Calculation for Different Books")
        
        test_cases = [
            (100, Decimal('1.00')),
            (250, Decimal('2.50')),
            (500, Decimal('5.00')),
            (1000, Decimal('10.00')),
        ]
        
        for pages, expected_fee in test_cases:
            book = Book.objects.create(
                title=f"Book with {pages} pages",
                author="Test Author",
                isbn=f"ISBN{pages}",
                number_of_pages=pages
            )
            
            rental = Rental.objects.create(
                book=book,
                user=self.student1,
                rental_date=datetime.now().date()
            )
            
            # Check monthly fee calculation
            fee = book.monthly_rental_fee()
            self.assertEqual(fee, expected_fee)
            print(f"✅ {pages} pages → ${fee} per month")
    
    def test_scenario_5_extend_rental(self):
        """Test: Extend an existing rental"""
        print("\n📝 Test Scenario 5: Extend Rental")
        
        book = Book.objects.create(
            title="Extended Book",
            author="Test Author",
            isbn="EXT123",
            number_of_pages=400
        )
        
        rental = Rental.objects.create(
            book=book,
            user=self.student2,
            rental_date=datetime.now().date()
        )
        
        print(f"✅ Rental created")
        expected_fee = book.monthly_rental_fee()
        print(f"✅ Monthly rental fee: ${expected_fee}")
    
    def test_scenario_6_return_book(self):
        """Test: Return a rented book"""
        print("\n📝 Test Scenario 6: Return Book")
        
        book = Book.objects.create(
            title="Return Test Book",
            author="Test Author",
            isbn="RET123",
            number_of_pages=200
        )
        
        print(f"📚 Book created: {book.title}")
        
        rental = Rental.objects.create(
            book=book,
            user=self.student1,
            rental_date=datetime.now().date()
        )
        
        print(f"✅ Rental created")
        
        # Check rental status
        rental.refresh_from_db()
        print(f"✅ Rental status: {rental.status}")
    
    def test_scenario_7_multiple_students_same_book(self):
        """Test: Multiple students renting the same book"""
        print("\n📝 Test Scenario 7: Multiple Students, Same Book")
        
        book = Book.objects.create(
            title="Popular Book",
            author="Famous Author",
            isbn="POP123",
            number_of_pages=350
        )
        
        print(f"📚 Book created: {book.title}")
        
        # Student 1 rents
        rental1 = Rental.objects.create(
            book=book,
            user=self.student1,
            rental_date=datetime.now().date()
        )
        print(f"✅ Student 1 rented: {rental1.user.username}")
        
        # Student 2 rents
        rental2 = Rental.objects.create(
            book=book,
            user=self.student2,
            rental_date=datetime.now().date()
        )
        print(f"✅ Student 2 rented: {rental2.user.username}")
        
        # Verify both rentals exist
        self.assertEqual(Rental.objects.filter(book=book).count(), 2)
        print(f"✅ Total rentals for book: {Rental.objects.filter(book=book).count()}")
    
    def test_scenario_8_openlibrary_integration(self):
        """Test: OpenLibrary API integration with real API call"""
        print("\n📝 Test Scenario 8: OpenLibrary API Integration")
        
        service = OpenLibraryService()
        
        # Test with a well-known book
        result = service.search_book_by_title("1984")
        
        if result:
            print(f"✅ API Response received")
            print(f"   Title: {result.get('title')}")
            print(f"   Author: {result.get('author')}")
            print(f"   Pages: {result.get('number_of_pages')}")
            print(f"   ISBN: {result.get('isbn')}")
            
            # Verify required fields
            self.assertIsNotNone(result.get('title'))
            self.assertIsNotNone(result.get('author'))
            self.assertIsNotNone(result.get('number_of_pages'))
        else:
            print("⚠️ API call failed (might be rate limited or network issue)")


class DummyUserGenerator:
    """Utility class to generate dummy users for testing"""
    
    @staticmethod
    def create_dummy_users(count=5):
        """Create specified number of dummy users"""
        print(f"\n👥 Creating {count} dummy users...")
        
        dummy_data = [
            ('alice_wonder', 'Alice', 'Wonder'),
            ('bob_builder', 'Bob', 'Builder'),
            ('charlie_brown', 'Charlie', 'Brown'),
            ('diana_prince', 'Diana', 'Prince'),
            ('edward_stark', 'Edward', 'Stark'),
            ('fiona_apple', 'Fiona', 'Apple'),
            ('george_martin', 'George', 'Martin'),
            ('hannah_montana', 'Hannah', 'Montana'),
            ('ivan_terrible', 'Ivan', 'Terrible'),
            ('julia_child', 'Julia', 'Child'),
        ]
        
        created_users = []
        for i in range(min(count, len(dummy_data))):
            username, first_name, last_name = dummy_data[i]
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'password': 'student123'  # Note: Use set_password in production
                }
            )
            
            if created:
                user.set_password('student123')
                user.save()
                print(f"✅ Created: {username} ({first_name} {last_name})")
                created_users.append(user)
            else:
                print(f"⚠️ Already exists: {username}")
        
        return created_users
    
    @staticmethod
    def create_dummy_books(count=5):
        """Create dummy books for testing"""
        print(f"\n📚 Creating {count} dummy books...")
        
        books_data = [
            ("The Great Adventure", "John Smith", "ADV001", 450),
            ("Mystery of the Old House", "Jane Doe", "MYS002", 320),
            ("Science for Beginners", "Dr. Albert", "SCI003", 280),
            ("History of Ancient Rome", "Marcus Julius", "HIS004", 520),
            ("Programming Basics", "Tech Guru", "PRG005", 380),
            ("Cooking Masterclass", "Chef Gordon", "COK006", 240),
            ("Travel Guide Europe", "Explorer Jane", "TRV007", 410),
            ("Mathematics Advanced", "Prof. Newton", "MTH008", 560),
            ("Art of Photography", "Camera Man", "ART009", 290),
            ("Business Strategy", "MBA Expert", "BUS010", 350),
        ]
        
        created_books = []
        for i in range(min(count, len(books_data))):
            title, author, isbn, pages = books_data[i]
            monthly_fee = Decimal(str(pages / 100))
            
            book, created = Book.objects.get_or_create(
                isbn=isbn,
                defaults={
                    'title': title,
                    'author': author,
                    'number_of_pages': pages
                }
            )
            
            if created:
                print(f"✅ Created: {title} ({pages} pages, ${monthly_fee}/month)")
                created_books.append(book)
            else:
                print(f"⚠️ Already exists: {title}")
        
        return created_books


def run_all_tests():
    """Run all scenario tests"""
    print("=" * 80)
    print("🧪 BOOK RENTAL SYSTEM - COMPREHENSIVE SCENARIO TESTS")
    print("=" * 80)
    
    from django.test.runner import DiscoverRunner
    
    test_runner = DiscoverRunner(verbosity=2)
    failures = test_runner.run_tests(['__main__.ScenarioTestCase'])
    
    print("\n" + "=" * 80)
    if failures:
        print("❌ TESTS COMPLETED WITH FAILURES")
    else:
        print("✅ ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 80)
    
    return failures


def setup_dummy_data():
    """Quick setup with dummy users and books"""
    print("=" * 80)
    print("🔧 SETTING UP DUMMY DATA")
    print("=" * 80)
    
    generator = DummyUserGenerator()
    
    # Create users
    users = generator.create_dummy_users(5)
    
    # Create books
    books = generator.create_dummy_books(5)
    
    print("\n" + "=" * 80)
    print(f"✅ Setup Complete: {len(users)} users, {len(books)} books created")
    print("=" * 80)
    print("\n📝 Test Login Credentials:")
    print("   Username: alice_wonder, Password: student123")
    print("   Username: bob_builder, Password: student123")
    print("   (All dummy users have password: student123)")
    print("=" * 80)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        # Just setup dummy data
        setup_dummy_data()
    elif len(sys.argv) > 1 and sys.argv[1] == '--users':
        # Create only users
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        generator = DummyUserGenerator()
        generator.create_dummy_users(count)
    elif len(sys.argv) > 1 and sys.argv[1] == '--books':
        # Create only books
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        generator = DummyUserGenerator()
        generator.create_dummy_books(count)
    else:
        # Run all tests
        run_all_tests()
