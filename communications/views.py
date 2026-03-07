from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import SMSLog, EmailLog, MessageTemplate
from .utils import send_sms, send_email_notification

@login_required
@permission_required('accounts.manage_communications', raise_exception=True)
def send_bulk_message(request):
    if request.method == 'POST':
        message_type = request.POST.get('message_type') # 'sms' or 'email'
        recipients_text = request.POST.get('recipients') # comma separated
        subject = request.POST.get('subject', '')
        body = request.POST.get('body')
        
        if not recipients_text or not body:
            messages.error(request, "Recipients and message body are required.")
            return redirect('send_bulk_message')
            
        recipients = [r.strip() for r in recipients_text.split(',') if r.strip()]
        success_count = 0
        fail_count = 0
        
        for recipient in recipients:
            if message_type == 'sms':
                if send_sms(recipient, body, request.user):
                    success_count += 1
                else:
                    fail_count += 1
            elif message_type == 'email':
                if send_email_notification(recipient, subject, body, request.user):
                    success_count += 1
                else:
                    fail_count += 1
                    
        messages.success(request, f"Sent {success_count} {message_type}(s) successfully. Failed: {fail_count}.")
        return redirect('message_logs')
        
    templates = MessageTemplate.objects.all()
    return render(request, 'communications/send_message.html', {'templates': templates})

@login_required
@permission_required('accounts.manage_communications', raise_exception=True)
def message_logs(request):
    sms_logs = SMSLog.objects.all().order_by('-sent_at')[:100]
    email_logs = EmailLog.objects.all().order_by('-sent_at')[:100]
    
    return render(request, 'communications/message_logs.html', {
        'sms_logs': sms_logs,
        'email_logs': email_logs,
    })
