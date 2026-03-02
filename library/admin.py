from django.contrib import admin
from .models import Author, BookCategory, Book, BookIssue

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'barcode', 'author', 'category', 'available_copies', 'total_copies')
    search_fields = ('title', 'isbn', 'barcode', 'author__name')
    list_filter = ('category', 'publisher')

@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'issue_date', 'due_date', 'status', 'fine_amount')
    list_filter = ('status', 'issue_date')
    search_fields = ('book__title', 'book__barcode', 'user__username', 'user__first_name')
