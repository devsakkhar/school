from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'john.doe@example.com'}),
            'image': forms.FileInput(attrs={'class': 'account-file-input', 'hidden': True, 'accept': 'image/png, image/jpeg'}),
        }

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password('123456')  # Default password
        if commit:
            user.save()
        return user

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
class RoleForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 10}),
        required=False,
        help_text='Hold down "Control", or "Command" on a Mac, to select more than one.'
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Principal'}),
        }

from .models import Notice

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'file_attachment', 'target_audience', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'file_attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'target_audience': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
