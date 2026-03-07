import requests
from django.conf import settings
from .models import SMSLog, EmailLog, MessageTemplate
from django.core.mail import send_mail

def send_sms(recipient_number, message_body, user=None):
    """
    Mock SMS Gateway Integration.
    In production, replace with Nexmo, Twilio, or local SMS API.
    """
    # Create the log entry as pending
    log = SMSLog.objects.create(
        recipient_number=recipient_number,
        message=message_body,
        sent_by=user,
        status='Pending'
    )
    
    try:
        # Example API call structure (commented out):
        # response = requests.post("https://api.smsprovider.com/send", data={
        #     'apikey': settings.SMS_API_KEY,
        #     'to': recipient_number,
        #     'message': message_body
        # })
        
        # Simulate Success
        log.status = 'Sent'
        log.api_response = 'Mock Success 200 OK'
        log.save()
        return True
        
    except Exception as e:
        log.status = 'Failed'
        log.api_response = str(e)
        log.save()
        return False

def send_templated_sms(template_name, recipient_number, context_dict, user=None):
    try:
        template = MessageTemplate.objects.get(name=template_name)
        message_body = template.content.format(**context_dict)
        return send_sms(recipient_number, message_body, user)
    except MessageTemplate.DoesNotExist:
        # Fallback if template doesn't exist
        print(f"Template {template_name} not found.")
        return False
    except KeyError as e:
        print(f"Missing context variable for template: {e}")
        return False

def send_email_notification(recipient_email, subject, body, user=None):
    """
    Standard Django Email sending wrapped with logging.
    """
    log = EmailLog.objects.create(
        recipient_email=recipient_email,
        subject=subject,
        body=body,
        sent_by=user,
        status='Pending'
    )
    
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@school.com',
            [recipient_email],
            fail_silently=False,
        )
        log.status = 'Sent'
        log.save()
        return True
    except Exception as e:
        log.status = 'Failed'
        log.save()
        return False
