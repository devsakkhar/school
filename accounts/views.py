from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib import messages
from django.contrib.auth.models import Group
from .models import CustomUser
from .forms import ProfileUpdateForm, RoleForm, CustomUserCreationForm, CustomUserChangeForm

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    context = {
        'form': form
    }
    return render(request, 'accounts/profile_edit.html', context)

# -------------------------------------------------------------
# Role Management Views
# -------------------------------------------------------------
def is_admin(user):
    return user.is_superuser

from collections import defaultdict
from django.contrib.auth.models import Permission

def get_grouped_permissions():
    perms = Permission.objects.exclude(content_type__app_label__in=['admin', 'contenttypes', 'sessions'])
    grouped = defaultdict(list)
    for p in perms:
        model_name = p.content_type.model.replace('_', ' ').title()
        app_name = p.content_type.app_label.title()
        group_name = f"{app_name} - {model_name}"
        action = p.codename.split('_')[0] # add, change, delete, view
        grouped[group_name].append({
            'id': p.id,
            'name': p.name,
            'codename': p.codename,
            'action': action
        })
    return grouped.items()

@login_required
@permission_required('accounts.manage_roles', raise_exception=True)
def role_list(request):
    roles = Group.objects.all()
    return render(request, 'accounts/roles/role_list.html', {'roles': roles})

@login_required
@permission_required('accounts.manage_roles', raise_exception=True)
def role_create(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Role created successfully!')
            return redirect('role_list')
    else:
        form = RoleForm()
        
    context = {
        'form': form, 
        'action': 'Create',
        'grouped_permissions': get_grouped_permissions(),
        'role_permissions': []
    }
    return render(request, 'accounts/roles/role_form.html', context)

@login_required
@permission_required('accounts.manage_roles', raise_exception=True)
def role_update(request, pk):
    role = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, 'Role updated successfully!')
            return redirect('role_list')
    else:
        form = RoleForm(instance=role)
        
    context = {
        'form': form, 
        'action': 'Update',
        'grouped_permissions': get_grouped_permissions(),
        'role_permissions': list(role.permissions.values_list('id', flat=True))
    }
    return render(request, 'accounts/roles/role_form.html', context)

@login_required
@permission_required('accounts.manage_roles', raise_exception=True)
def role_delete(request, pk):
    role = get_object_or_404(Group, pk=pk)
    
    # 1. Safeguard: Prevent deleting essential roles
    essential_roles = ['admin', 'administrator', 'teacher', 'student']
    if role.name.lower() in essential_roles:
        messages.error(request, f"Cannot delete the essential role: {role.name}.")
        return redirect('role_list')

    # 2. Safeguard: Prevent deleting roles that users are currently assigned to
    if role.users.exists():
        messages.error(request, f"Cannot delete role '{role.name}' because {role.users.count()} user(s) are currently assigned to it.")
        return redirect('role_list')

    if request.method == 'POST':
        role.delete()
        messages.success(request, 'Role deleted successfully!')
        return redirect('role_list')
    return render(request, 'accounts/roles/role_confirm_delete.html', {'role': role})

# User Management
@login_required
@permission_required('accounts.manage_users', raise_exception=True)
def user_list(request):
    search_query = request.GET.get('q', '')
    users = CustomUser.objects.all().order_by('-date_joined')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(role__name__icontains=search_query)
        )
        
    paginator = Paginator(users, 10) # 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/users/user_list.html', {'users': page_obj, 'search_query': search_query})

@login_required
@permission_required('accounts.manage_users', raise_exception=True)
def user_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # If the role is selected, update it explicitly (CustomUser model handles this)
            messages.success(request, 'User created successfully!')
            return redirect('user_list')
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'accounts/users/user_form.html', {'form': form, 'action': 'Create'})

@login_required
@permission_required('accounts.manage_users', raise_exception=True)
def user_update(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully!')
            return redirect('user_list')
    else:
        form = CustomUserChangeForm(instance=user)
        
    return render(request, 'accounts/users/user_form.html', {'form': form, 'action': 'Update'})

@login_required
@permission_required('accounts.manage_users', raise_exception=True)
def user_delete(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    # Prevent users from deleting themselves or other admins accidentally
    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('user_list')
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('user_list')
    return render(request, 'accounts/users/user_confirm_delete.html', {'user_obj': user})
