"""
Quick script to create dummy users and books for testing
Usage:
    python create_dummy_users.py               # Create 5 users and 5 books
    python create_dummy_users.py --users 10    # Create 10 users only
    python create_dummy_users.py --books 10    # Create 10 books only
    python create_dummy_users.py --all 10      # Create 10 users and 10 books
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_rental_system.settings')
django.setup()

from django.contrib.auth.models import User
from rentals.models import Book
from decimal import Decimal


def create_users(count=5):
    """Create dummy student users"""
    print(f"\n{'='*60}")
    print(f"👥 CREATING {count} DUMMY USERS")
    print('='*60)
    
    user_data = [
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
        ('kevin_hart', 'Kevin', 'Hart'),
        ('lisa_simpson', 'Lisa', 'Simpson'),
        ('michael_scott', 'Michael', 'Scott'),
        ('nancy_drew', 'Nancy', 'Drew'),
        ('oliver_twist', 'Oliver', 'Twist'),
    ]
    
    created_count = 0
    for i in range(min(count, len(user_data))):
        username, first_name, last_name = user_data[i]
        
        if User.objects.filter(username=username).exists():
            print(f"⚠️  {username:20} - Already exists")
        else:
            user = User.objects.create_user(
                username=username,
                password='student123',
                first_name=first_name,
                last_name=last_name
            )
            print(f"✅ {username:20} - Created ({first_name} {last_name})")
            created_count += 1
    
    print('='*60)
    print(f"✅ Created {created_count} new users")
    print(f"📝 All users have password: student123")
    print('='*60)


def create_books(count=5):
    """Create dummy books"""
    print(f"\n{'='*60}")
    print(f"📚 CREATING {count} DUMMY BOOKS")
    print('='*60)
    
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
        ("Digital Marketing", "Social Media Pro", "MKT011", 310),
        ("Psychology Basics", "Dr. Mind", "PSY012", 420),
        ("Physics for Everyone", "Einstein Jr", "PHY013", 480),
        ("Creative Writing", "Author Best", "WRT014", 270),
        ("Financial Freedom", "Money Guru", "FIN015", 390),
    ]
    
    created_count = 0
    for i in range(min(count, len(books_data))):
        title, author, isbn, pages = books_data[i]
        monthly_fee = Decimal(str(pages / 100))
        
        if Book.objects.filter(isbn=isbn).exists():
            print(f"⚠️  {title:30} - Already exists")
        else:
            book = Book.objects.create(
                title=title,
                author=author,
                isbn=isbn,
                number_of_pages=pages
            )
            print(f"✅ {title:30} - {pages:3} pages (${monthly_fee}/mo)")
            created_count += 1
    
    print('='*60)
    print(f"✅ Created {created_count} new books")
    print('='*60)


def create_admin():
    """Create admin user if doesn't exist"""
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        print("\n✅ Admin user created: admin / admin123")
    else:
        print("\n✅ Admin user already exists: admin / admin123")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔧 DUMMY DATA GENERATOR FOR BOOK RENTAL SYSTEM")
    print("="*60)
    
    # Parse arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        
        if arg == '--users':
            create_admin()
            create_users(count)
        elif arg == '--books':
            create_books(count)
        elif arg == '--all':
            create_admin()
            create_users(count)
            create_books(count)
        else:
            print(f"\n❌ Unknown argument: {arg}")
            print("\nUsage:")
            print("  python create_dummy_users.py               # Default: 5 users + 5 books")
            print("  python create_dummy_users.py --users 10    # Create 10 users only")
            print("  python create_dummy_users.py --books 10    # Create 10 books only")
            print("  python create_dummy_users.py --all 10      # Create 10 users + 10 books")
    else:
        # Default: create both
        create_admin()
        create_users(5)
        create_books(5)
    
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    print("\n📝 Quick Reference:")
    print("   Admin: admin / admin123")
    print("   Students: alice_wonder, bob_builder, etc. / student123")
    print("   Server: python manage.py runserver")
    print("   URL: http://127.0.0.1:8000/")
    print("="*60 + "\n")
