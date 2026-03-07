from django.db import models
from django.conf import settings

class MessageTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="e.g., 'Admission Approval', 'Fee Reminder'")
    subject = models.CharField(max_length=255, blank=True, help_text="Used for Email subjects")
    content = models.TextField(help_text="Use {name}, {date}, {amount} as placeholders.")
    
    def __str__(self):
        return self.name

class SMSLog(models.Model):
    recipient_number = models.CharField(max_length=20)
    message = models.TextField()
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Pending')
    api_response = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"SMS to {self.recipient_number} at {self.sent_at}"

class EmailLog(models.Model):
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Pending')
    
    def __str__(self):
        return f"Email to {self.recipient_email} at {self.sent_at}"
