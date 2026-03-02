from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, permission_required
from .models import Author, BookCategory
from .forms import AuthorForm, BookCategoryForm

@login_required
@permission_required('accounts.manage_academic_settings', raise_exception=True)
@require_POST
def api_add_author(request):
    form = AuthorForm(request.POST)
    if form.is_valid():
        author = form.save()
        return JsonResponse({'success': True, 'id': author.id, 'name': author.name})
    return JsonResponse({'success': False, 'errors': form.errors})

@login_required
@permission_required('accounts.manage_academic_settings', raise_exception=True)
@require_POST
def api_add_category(request):
    form = BookCategoryForm(request.POST)
    if form.is_valid():
        category = form.save()
        return JsonResponse({'success': True, 'id': category.id, 'name': category.name})
    return JsonResponse({'success': False, 'errors': form.errors})
