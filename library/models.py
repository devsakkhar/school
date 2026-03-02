from django.db import models
from django.conf import settings
from datetime import date
import uuid

class Author(models.Model):
    name = models.CharField(max_length=200)
    biography = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class BookCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Book Categories"

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    barcode = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Scan or enter book barcode")
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name='books')
    category = models.ForeignKey(BookCategory, on_delete=models.SET_NULL, null=True, related_name='books')
    publisher = models.CharField(max_length=200, blank=True)
    publication_year = models.IntegerField(null=True, blank=True)
    
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    
    location = models.CharField(max_length=100, help_text="e.g., Rack A, Shelf 2", blank=True)
    
    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        # Auto-generate barcode if none provided
        if not self.barcode:
            self.barcode = "LIB-" + str(uuid.uuid4().hex[:8]).upper()
        super().save(*args, **kwargs)

class BookIssue(models.Model):
    STATUS_CHOICES = [
        ('Issued', 'Issued'),
        ('Returned', 'Returned'),
        ('Lost', 'Lost'),
    ]
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='borrowed_books', help_text="Student or Staff who borrowed the book")
    
    issue_date = models.DateField(default=date.today)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Issued')
    
    # Fine details
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    fine_paid = models.BooleanField(default=False)
    
    def calculate_fine(self):
        """ Calculate fine based on due date if returned late. E.g., 5 currency units per day. """
        if self.status == 'Returned' and self.return_date and self.return_date > self.due_date:
            days_late = (self.return_date - self.due_date).days
            return days_late * 5.00 # 5 Taka / unit per day
        elif self.status == 'Issued' and date.today() > self.due_date:
            days_late = (date.today() - self.due_date).days
            return days_late * 5.00
        return 0.00
        
    def __str__(self):
        return f"{self.book.title} issued to {self.user.get_full_name() or self.user.username}"
