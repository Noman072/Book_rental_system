from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class Book(models.Model):
    """
    Represents a book available for rental.
    Book details are fetched from OpenLibrary API.
    """
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    isbn = models.CharField(max_length=20, blank=True, null=True)
    number_of_pages = models.IntegerField(default=0)
    cover_image_url = models.URLField(blank=True, null=True)
    openlibrary_key = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def monthly_rental_fee(self):
        """
        Calculate monthly rental fee based on page count.
        Formula: number_of_pages / 100
        """
        if self.number_of_pages > 0:
            return Decimal(self.number_of_pages) / Decimal(100)
        return Decimal('0.00')


class Rental(models.Model):
    """
    Represents a book rental by a student.
    First month is free, subsequent months are charged based on book's page count.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rentals')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='rentals')
    rental_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    months_extended = models.IntegerField(default=0)
    total_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-rental_date']

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    def save(self, *args, **kwargs):
        # Set initial due date to 1 month from rental date if not set
        if not self.due_date:
            self.due_date = self.rental_date + timedelta(days=30)
        super().save(*args, **kwargs)

    def calculate_charges(self):
        """
        Calculate total charges based on months extended.
        First month is free, subsequent months are charged.
        """
        if self.months_extended > 0:
            monthly_fee = self.book.monthly_rental_fee()
            self.total_charges = monthly_fee * self.months_extended
        else:
            self.total_charges = Decimal('0.00')
        return self.total_charges

    def extend_rental(self, months=1):
        """
        Extend the rental period by specified number of months.
        Automatically calculates and applies charges.
        """
        self.months_extended += months
        self.due_date += timedelta(days=30 * months)
        self.calculate_charges()
        self.save()
        return self.total_charges

    def is_overdue(self):
        """Check if rental is overdue."""
        if self.status == 'returned':
            return False
        return timezone.now() > self.due_date

    def days_remaining(self):
        """Calculate days remaining until due date."""
        if self.status == 'returned':
            return 0
        delta = self.due_date - timezone.now()
        return max(0, delta.days)
