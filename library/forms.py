from django import forms
from .models import Book, BookIssue, Author, BookCategory
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'biography']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'biography': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class BookCategoryForm(forms.ModelForm):
    class Meta:
        model = BookCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'isbn', 'barcode', 'author', 'category', 'publisher', 'publication_year', 'total_copies', 'available_copies', 'location']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

class BookIssueForm(forms.ModelForm):
    class Meta:
        model = BookIssue
        fields = ['book', 'user', 'issue_date', 'due_date']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-select'}),
            'user': forms.Select(attrs={'class': 'form-select'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control flatpickr', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control flatpickr', 'type': 'date'}),
        }
