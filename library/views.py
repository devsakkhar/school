from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone
from .models import Book, BookCategory, Author, BookIssue
from .forms import BookForm, BookCategoryForm, AuthorForm, BookIssueForm
from django.db.models import Q
from datetime import date

# ══════════════════════════════════════════════════════════
# Admin / Librarian Views
# ══════════════════════════════════════════════════════════

@login_required
@permission_required('accounts.manage_academic_settings', raise_exception=True)
def library_dashboard(request):
    total_books = Book.objects.count()
    total_issued = BookIssue.objects.filter(status='Issued').count()
    overdue_issues = BookIssue.objects.filter(status='Issued', due_date__lt=date.today()).count()
    
    return render(request, 'library/dashboard.html', {
        'total_books': total_books,
        'total_issued': total_issued,
        'overdue_issues': overdue_issues
    })

@login_required
@permission_required('accounts.manage_academic_settings', raise_exception=True)
def book_list(request):
    query = request.GET.get('q', '')
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) | 
            Q(author__name__icontains=query) | 
            Q(isbn__icontains=query) | 
            Q(barcode__icontains=query)
        ).select_related('author', 'category')
    else:
        books = Book.objects.select_related('author', 'category').all()
        
    return render(request, 'library/book_list.html', {'books': books, 'query': query})

@login_required
@permission_required('accounts.manage_academic_settings', raise_exception=True)
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book added successfully.')
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form, 'action': 'Add'})

@login_required
@permission_required('accounts.manage_academic_settings', raise_exception=True)
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully.')
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'library/book_form.html', {'form': form, 'action': 'Edit'})

@login_required
@permission_required('accounts.manage_academic_settings', raise_exception=True)
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully.')
        return redirect('book_list')
    return render(request, 'library/book_confirm_delete.html', {'book': book})


# ══════════════════════════════════════════════════════════
# Book Issue / Return Views
# ══════════════════════════════════════════════════════════

@login_required
@permission_required('accounts.manage_academic_settings', raise_exception=True)
def issue_list(request):
    issues = BookIssue.objects.select_related('book', 'user').all().order_by('-issue_date')
    return render(request, 'library/issue_list.html', {'issues': issues})

@login_required
@permission_required('accounts.manage_academic_settings', raise_exception=True)
def issue_create(request):
    if request.method == 'POST':
        form = BookIssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            book = issue.book
            
            if book.available_copies > 0:
                book.available_copies -= 1
                book.save()
                issue.save()
                messages.success(request, f'Book "{book.title}" issued successfully.')
                return redirect('issue_list')
            else:
                messages.error(request, 'This book is currently out of stock.')
    else:
        # If barcode scanned and passed via GET
        barcode = request.GET.get('barcode')
        initial_data = {'issue_date': date.today()}
        if barcode:
            book = Book.objects.filter(barcode=barcode).first()
            if book:
                initial_data['book'] = book
            else:
                messages.warning(request, 'No book found with the scanned barcode.')
                
        form = BookIssueForm(initial=initial_data)
        
    return render(request, 'library/issue_form.html', {'form': form})

@login_required
@permission_required('accounts.manage_academic_settings', raise_exception=True)
def issue_return(request, pk):
    issue = get_object_or_404(BookIssue, pk=pk)
    if issue.status == 'Returned':
        messages.info(request, 'Book is already returned.')
        return redirect('issue_list')
        
    if request.method == 'POST':
        issue.return_date = date.today()
        issue.status = 'Returned'
        issue.fine_amount = issue.calculate_fine()
        
        # Increase available copies
        book = issue.book
        book.available_copies += 1
        
        issue.save()
        book.save()
        messages.success(request, f'Book returned successfully. Total Fine: ৳{issue.fine_amount}')
        return redirect('issue_list')
        
    fine_estimate = issue.calculate_fine()
    return render(request, 'library/issue_return_confirm.html', {'issue': issue, 'fine_estimate': fine_estimate})

@login_required
@permission_required('accounts.manage_academic_settings', raise_exception=True)
def fine_list(request):
    issues_with_fines = BookIssue.objects.filter(fine_amount__gt=0).order_by('fine_paid', '-return_date')
    return render(request, 'library/fine_list.html', {'issues': issues_with_fines})

@login_required
@permission_required('accounts.manage_academic_settings', raise_exception=True)
def fine_pay(request, pk):
    issue = get_object_or_404(BookIssue, pk=pk)
    if issue.fine_amount > 0 and not issue.fine_paid:
        issue.fine_paid = True
        issue.save()
        messages.success(request, f'Fine of ৳{issue.fine_amount} paid successfully.')
    return redirect('fine_list')

# ══════════════════════════════════════════════════════════
# Member/Student View
# ══════════════════════════════════════════════════════════
@login_required
def my_books(request):
    issues = BookIssue.objects.filter(user=request.user).select_related('book').order_by('-issue_date')
    return render(request, 'library/my_books.html', {'issues': issues})
