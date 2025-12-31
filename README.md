# Book Rental System

## Executive Summary

A Django web application designed for efficient management of student book rentals. The system features real-time AJAX book search, automatic fee calculation based on page count, and seamless OpenLibrary API integration. Built with modern web technologies and comprehensive testing, this solution streamlines the entire rental workflow from book discovery to return processing.

**Test Status**: ✅ All 8 scenario tests passing  
**API Integration**: ✅ OpenLibrary 2-step process (optimized for accuracy)  
**Code Coverage**: ✅ Business logic, API integration, and end-to-end workflows  
**Ready for**: Development review and production deployment preparation

---

## Quick Demo (For testing)

**Get Started in 3 Steps:**

```powershell
# 1. Setup (creates admin + 10 test users + 10 books)
python create_dummy_users.py --all 10

# 2. Run tests to verify everything works
python unit_test.py

# 3. Start the server
python manage.py runserver
```

**Then visit**: http://127.0.0.1:8000/

**Login with**: `admin` / `admin123`

**Try This:**
1. Click "New Rental" in navigation
2. Select a student (e.g., alice_wonder)
3. Type "Pride and Prejudice" in the book search
4. Watch the real-time AJAX search in action (blue→green border)
5. See the book preview with cover, author, pages, and auto-calculated fee
6. Click "Create Rental" to complete

**Test Results**: All 8 scenarios pass ✅ (see Test Results Summary below)

---

## Key Features

### Core Functionality
- **Real-Time AJAX Book Search**: Search for books as you type with 800ms debouncing and live results from OpenLibrary
- **OpenLibrary Integration**: Automatically fetch book details including title, author, pages, ISBN, and cover images using a 2-step API process for maximum accuracy
- **Intelligent Fee Calculation**: First month free, then automatic calculation at pages ÷ 100 per month
- **Modern Admin Dashboard**: Custom-built admin interface with comprehensive rental management and real-time statistics
- **Student Management**: Track all rentals, charges, and status for each student with detailed reporting
- **Rental Extensions**: Extend rental periods with automatic charge calculation and fee tracking
- **Book Returns**: Process returns with automatic inventory updates and status management



## Business Rules

1. **Free First Month**: Students can rent any book for the first month at no charge
2. **Monthly Fee Formula**: After the first month, the fee is calculated as:
   ```
   Monthly Fee = Number of Pages ÷ 100
   ```
   Example: A 300-page book costs $3.00 per month after the first month
3. **Cumulative Charges**: Extensions accumulate charges based on the monthly fee

## Technology Stack

- **Framework**: Django 3.2.8
- **Language**: Python 3.10.11
- **Database**: SQLite (development)
- **API Integration**: OpenLibrary Search API + Books API (2-step process)
- **Testing**: Django TestCase + scenario-based comprehensive tests
- **Authentication**: Django built-in auth with custom login templates

## Architecture Highlights

### AJAX Real-Time Search
- **Debouncing**: 800ms delay after user stops typing
- **Visual Feedback**: Loading, success, and error states with color-coded inputs
- **Book Preview**: Live preview card with cover image, author, pages, and calculated fee
- **JSON Endpoint**: RESTful API at `/api/search-book/`

### OpenLibrary Integration
- **Two-Step Process**: 
  1. Search by title using `/search.json?q=<title>`
  2. Fetch detailed edition data using `/api/books?bibkeys=OLID:<key>`
- **Fallback Logic**: Handles both `edition_key` and `cover_edition_key`
- **Error Handling**: Graceful degradation when API is unavailable

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## Quick Start

### Option 1: Complete Setup with Dummy Data

```powershell
# 1. Activate virtual environment
.venv\Scripts\Activate.ps1

# 2. Run migrations
python manage.py migrate

# 3. Create admin and dummy data (10 users + 10 books)
python create_dummy_users.py --all 10

# 4. Start server
python manage.py runserver
```

**Default Credentials:**
- Admin: `admin` / `admin123`
- Students: `alice_wonder`, `bob_builder`, etc. / `student123`

### Option 2: Manual Setup

```powershell
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. Create superuser
python manage.py createsuperuser

# 5. Start server
python manage.py runserver
```

Access the application at: **http://127.0.0.1:8000/**

## Usage Guide

### Login & Dashboard

1. Navigate to: **http://127.0.0.1:8000/**
2. Log in with admin credentials (redirects to admin dashboard)
3. Dashboard displays:
   - Total books, students, and rentals
   - Active rentals count
   - Recent rental activity

### Creating a New Rental (AJAX Search)

1. Click **"New Rental"** from the navigation menu
2. Select a student from the dropdown
3. **Start typing a book title** in the search field (e.g., "Pride and Prejudice")
4. Wait 800ms - the system will automatically search OpenLibrary
5. Visual feedback:
   - 🔵 Blue border = Searching...
   - 🟢 Green border = Book found!
   - 🔴 Red border = Error or not found
6. Review the book preview card showing:
   - Cover image
   - Title and author
   - Number of pages
   - Calculated monthly fee (pages ÷ 100)
7. Click **"Create Rental"** to confirm
8. System will:
   - Create or retrieve the book record
   - Create the rental with 30-day free period
   - Show success message

### Viewing All Rentals

1. Click **"View All Rentals"** from navigation
2. Filter by status: Active, Returned, Overdue
3. Search by student name or book title
4. See rental details:
   - Student name
   - Book title
   - Rental date and due date
   - Status (color-coded)
   - Total charges
   - Actions (extend, return)

## Dummy Data Generation

### Quick Commands

```powershell
# Create 10 users + 10 books + admin
python create_dummy_users.py --all 10

# Create only 15 users
python create_dummy_users.py --users 15

# Create only 8 books
python create_dummy_users.py --books 8

# Default: 5 users + 5 books
python create_dummy_users.py
```

### Generated Users
- **Usernames**: alice_wonder, bob_builder, charlie_brown, diana_prince, etc.


### Generated Books
Sample books with realistic page counts:
- The Great Adventure (450 pages → $4.50/month)
- Mystery of the Old House (320 pages → $3.20/month)
- Science for Beginners (280 pages → $2.80/month)
- And more...

## Project Structure

```
book_rental_system/
├── book_rental_system/          # Django project configuration
│   ├── settings.py              # Settings with LOGIN_REDIRECT_URL
│   ├── urls.py                  # Main URL routing
│   └── wsgi.py                  # WSGI configuration
├── rentals/                     # Main application
│   ├── models.py                # Book & Rental models with business logic
│   ├── views.py                 # Views including AJAX endpoint
│   ├── urls.py                  # App URL patterns
│   ├── services.py              # OpenLibrary API service (2-step process)
│   ├── forms.py                 # Django forms
│   ├── admin.py                 # Custom admin configuration
│   ├── tests.py                 # Django unit tests
│   ├── templates/
│   │   └── rentals/
│   │       ├── login.html       # Custom login page
│   │       └── admin/
│   │           ├── base.html
│   │           ├── dashboard.html
│   │           ├── new_rental.html    # AJAX search interface
│   │           ├── rental_list.html
│   │           ├── extend_rental.html
│   │           ├── student_dashboard.html
│   │           └── book_list.html
│   └── migrations/              # Database migrations
├── unit_test.py                 # Comprehensive scenario tests
├── create_dummy_users.py        # Dummy data generator
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── db.sqlite3                   # SQLite database (generated)
└── README.md                    # This file
```

## Models

### Book Model
- `title`: Book title
- `author`: Author name
- `isbn`: ISBN number
- `number_of_pages`: Page count (used for fee calculation)
- `cover_image_url`: Cover image from OpenLibrary
- `openlibrary_key`: OpenLibrary reference key

### Rental Model
- `user`: Foreign key to Django User (student)
- `book`: Foreign key to Book
- `rental_date`: When the rental started
- `due_date`: When the rental is due
- `return_date`: When the book was returned (nullable)
- `status`: Current status (active, returned, overdue)
- `months_extended`: Number of months extended beyond free month
- `total_charges`: Accumulated charges

## Test Results Summary

**All Comprehensive Tests Passing** ✅

```
================================================================================
🧪 BOOK RENTAL SYSTEM - COMPREHENSIVE SCENARIO TESTS
================================================================================

Test Results: 8/8 Passed (100%)

✅ Test Scenario 1: Admin Login and Dashboard Access
   - Admin authentication successful
   - Dashboard loads with correct statistics

✅ Test Scenario 2: AJAX Book Search
   - Book found: Pride and Prejudice (Jane Austen, 282 pages, $2.82/month)
   - API integration working correctly

✅ Test Scenario 3: First Month Free Rental
   - Rental created successfully
   - First month marked as free

✅ Test Scenario 4: Fee Calculation Accuracy
   - 100 pages → $1.00/month ✓
   - 250 pages → $2.50/month ✓
   - 500 pages → $5.00/month ✓
   - 1000 pages → $10.00/month ✓

✅ Test Scenario 5: Rental Extension
   - Extension logic working correctly
   - Fees calculated accurately

✅ Test Scenario 6: Book Return Workflow
   - Return processed successfully
   - Status updated correctly

✅ Test Scenario 7: Multiple Students, Same Book
   - Concurrent rentals supported
   - 2 rentals tracked correctly

✅ Test Scenario 8: OpenLibrary API Integration
   - Real API call successful
   - Title: Nineteen Eighty-Four (George Orwell, 314 pages)

================================================================================
✅ ALL TESTS PASSED SUCCESSFULLY!
================================================================================
```

## Testing

### Comprehensive Scenario Tests

Run the full test suite with 8 real-world scenarios:

```powershell
python unit_test.py
```

**Test Coverage:**
1. ✅ Admin login and dashboard access
2. ✅ AJAX book search with live OpenLibrary API
3. ✅ First month free rental creation
4. ✅ Fee calculation for different page counts (100, 250, 500, 1000 pages)
5. ✅ Rental extension logic
6. ✅ Book return workflow
7. ✅ Multiple students renting same book
8. ✅ OpenLibrary API integration (real API call)

### Django Unit Tests

Run Django's built-in tests:

```powershell
python manage.py test rentals
```

### Test Options

```powershell
# Setup dummy data without running tests
python unit_test.py --setup

# Create only users
python unit_test.py --users

# Create only books
python unit_test.py --books
```



## Development & Deployment

### Local Development

```powershell
# Activate environment
.venv\Scripts\Activate.ps1

# Run development server
python manage.py runserver

# Run with specific port
python manage.py runserver 8080

# Access shell for debugging
python manage.py shell
```



## License

This project is created as a coding exercise for Rewardz (Singapore).

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review comprehensive test results: `python unit_test.py`
3. Django documentation: https://docs.djangoproject.com/
4. OpenLibrary API docs: https://openlibrary.org/developers/api
