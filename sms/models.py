from django.db import models
from django.conf import settings
from students.models import StudentClass

User = settings.AUTH_USER_MODEL


class SMSMessage(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed')]

    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    recipient_class = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, null=True, blank=True)
    recipient_status = models.CharField(max_length=20, blank=True)
    message = models.TextField()
    recipient_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    gateway_response = models.TextField(blank=True, help_text='API response from SMS gateway')

    def __str__(self):
        return f"SMS by {self.sent_by} on {self.sent_at:%Y-%m-%d} ({self.recipient_count} recipients)"

    class Meta:
        ordering = ['-sent_at']
