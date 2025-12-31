"""
Forms for the rentals app.
"""
from django import forms
from django.contrib.auth.models import User


class NewRentalForm(forms.Form):
    """
    Form for creating a new rental.
    """
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Select Student",
        help_text="Choose the student who will rent the book"
    )
    book_title = forms.CharField(
        max_length=255,
        label="Book Title",
        help_text="Enter the book title to search in OpenLibrary",
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., Harry Potter and the Philosopher\'s Stone',
            'size': 50
        })
    )


class ExtendRentalForm(forms.Form):
    """
    Form for extending an existing rental.
    """
    months = forms.IntegerField(
        min_value=1,
        max_value=12,
        initial=1,
        label="Number of Months",
        help_text="Enter the number of months to extend the rental"
    )
