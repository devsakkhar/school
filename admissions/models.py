from django.db import models
from django.conf import settings
from students.models import StudentClass

class AdmissionCampaign(models.Model):
    title = models.CharField(max_length=200)
    academic_year = models.CharField(max_length=20, help_text="e.g., 2026-2027")
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.academic_year})"


class AdmissionApplication(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    
    # Campaign info
    campaign = models.ForeignKey(AdmissionCampaign, on_delete=models.CASCADE, related_name='applications')
    applied_class = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, null=True, related_name='admission_applications')
    
    # Student Info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    blood_group = models.CharField(max_length=5, blank=True, null=True, choices=[
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')
    ])
    religion = models.CharField(max_length=50, blank=True, null=True)
    previous_school = models.CharField(max_length=200, blank=True, null=True)
    
    # Parent/Guardian Info
    father_name = models.CharField(max_length=150)
    mother_name = models.CharField(max_length=150)
    guardian_phone = models.CharField(max_length=20)
    guardian_email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    
    # Application Metadata
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    remarks = models.TextField(blank=True, null=True, help_text="Admin remarks")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.applied_class} ({self.campaign.academic_year})"
