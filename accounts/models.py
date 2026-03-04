from django.contrib.auth.models import AbstractUser, Group
from django.db import models

class Role(Group):
    class Meta:
        proxy = True
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

class CustomUser(AbstractUser):
    role = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name='users', help_text='The role assigned to this user.')
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    def __str__(self):
        role_name = self.role.name if self.role else "No Role"
        return f"{self.username} - {role_name}"

    class Meta:
        permissions = [
            ("manage_roles", "Can manage roles and permissions"),
            ("manage_users", "Can manage system users"),
            ("view_dashboard_stats", "Can view dashboard statistics"),
            ("manage_academic_settings", "Can manage classes, subjects, and exams"),
            ("manage_finances", "Can manage fees and staff salaries"),
        ]

class Notice(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    file_attachment = models.FileField(upload_to='notices/', blank=True, null=True)
    target_audience = models.CharField(
        max_length=50, 
        choices=[('All', 'All'), ('Students', 'Students'), ('Teachers', 'Teachers'), ('Staff', 'Staff')], 
        default='All'
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-date_posted']
        
    def __str__(self):
        return self.title
