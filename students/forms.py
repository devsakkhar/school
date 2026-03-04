from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Student, StudentClass, StudentSection, SchoolSettings, DisciplinaryRecord, AlumniProfile, Syllabus, LessonPlan

CustomUser = get_user_model()

class StudentCreationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    
    BLOOD_GROUP_CHOICES = [
        ('', 'Select Blood Group'),
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    blood_group = forms.ChoiceField(choices=BLOOD_GROUP_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))

    RELIGION_CHOICES = [
        ('', 'Select Religion'),
        ('Islam', 'Islam'),
        ('Hinduism', 'Hinduism'),
        ('Christianity', 'Christianity'),
        ('Buddhism', 'Buddhism'),
        ('Other', 'Other'),
    ]
    religion = forms.ChoiceField(choices=RELIGION_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Student
        fields = [
            'admission_number', 'admission_date', 'current_class', 'section', 'roll_number',
            'status', 'date_of_birth', 'gender', 'blood_group', 'religion',
            'present_address', 'permanent_address', 'phone_number',
            'father_name', 'father_phone', 'mother_name', 'mother_phone',
            'guardian_name', 'guardian_phone', 'guardian_relation', 'previous_school'
        ]
        widgets = {
            'admission_number': forms.TextInput(attrs={'class': 'form-control'}),
            'admission_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'current_class': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-control'}),
            'religion': forms.TextInput(attrs={'class': 'form-control'}),
            
            'present_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'permanent_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'father_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian_relation': forms.TextInput(attrs={'class': 'form-control'}),
            
            'previous_school': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['section'].queryset = StudentSection.objects.none()

        if 'current_class' in self.data:
            try:
                class_id = int(self.data.get('current_class'))
                self.fields['section'].queryset = StudentSection.objects.filter(student_class_id=class_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.current_class:
            self.fields['section'].queryset = self.instance.current_class.sections.order_by('name')

    def save(self, commit=True):
        student = super().save(commit=False)
        
        # Create user
        username = self.cleaned_data.get('email') # or generate one from admission_number
        user = CustomUser(
            username=self.cleaned_data.get('admission_number'), # Admission number as username is a good standard
            email=self.cleaned_data.get('email'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
        )
        if self.cleaned_data.get('image'):
            user.image = self.cleaned_data.get('image')
            
        user.set_password('123456') # Default password
        
        # Assign role
        try:
            student_group = Group.objects.get(name__iexact='Student')
            user.role = student_group
        except Group.DoesNotExist:
            pass # Handle gracefully or ensure 'setup_roles' is run
            
        if commit:
            user.save()
            student.user = user
            student.save()
        return student

class StudentChangeForm(StudentCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        student = super(forms.ModelForm, self).save(commit=False)

        user = student.user
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        
        if self.cleaned_data.get('image'):
            user.image = self.cleaned_data.get('image')
        
        if commit:
            user.save()
            student.save()
            
        return student

class SchoolSettingsForm(forms.ModelForm):
    class Meta:
        model = SchoolSettings
        fields = [
            'name', 'tagline', 'logo', 'signature',
            'phone', 'email', 'website',
            'address', 'city', 'district',
            'current_academic_year', 'established_year', 'affiliation',
            'principal_name', 'vice_principal_name',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MRM High School'}),
            'tagline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Knowledge · Character · Service'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'signature': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +880 1XXX-XXXXXX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'admin@school.edu'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://school.edu'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Street address...'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'current_academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2025-2026'}),
            'established_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1985'}),
            'affiliation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bangladesh Secondary and Higher Secondary Education Board'}),
            'principal_name': forms.TextInput(attrs={'class': 'form-control'}),
            'vice_principal_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class StudentClassForm(forms.ModelForm):
    class Meta:
        model = StudentClass
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Class 1'})
        }

class StudentSectionForm(forms.ModelForm):
    class Meta:
        model = StudentSection
        fields = ['student_class', 'name']
        widgets = {
            'student_class': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DisciplinaryRecordForm(forms.ModelForm):
    class Meta:
        model = DisciplinaryRecord
        fields = ['incident_date', 'title', 'description', 'action_taken', 'severity']
        widgets = {
            'incident_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'action_taken': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
        }

class AlumniProfileForm(forms.ModelForm):
    class Meta:
        model = AlumniProfile
        fields = ['graduation_year', 'current_profession', 'company_name', 'contact_email', 'contact_phone', 'higher_education_info', 'achievements']
        widgets = {
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'current_profession': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'higher_education_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'achievements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SyllabusForm(forms.ModelForm):
    class Meta:
        model = Syllabus
        fields = ['title', 'student_class', 'subject', 'academic_year', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'student_class': forms.Select(attrs={'class': 'form-select select2'}),
            'subject': forms.Select(attrs={'class': 'form-select select2'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2025-2026'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class LessonPlanForm(forms.ModelForm):
    class Meta:
        model = LessonPlan
        fields = ['title', 'student_class', 'subject', 'date', 'content', 'file_attachment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'student_class': forms.Select(attrs={'class': 'form-select select2'}),
            'subject': forms.Select(attrs={'class': 'form-select select2'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'file_attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }
