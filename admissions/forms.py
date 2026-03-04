from django import forms
from .models import AdmissionApplication

class AdmissionApplicationForm(forms.ModelForm):
    class Meta:
        model = AdmissionApplication
        exclude = ['campaign', 'application_date', 'status', 'remarks']
        widgets = {
            'applied_class': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'religion': forms.TextInput(attrs={'class': 'form-control'}),
            'previous_school': forms.TextInput(attrs={'class': 'form-control'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
