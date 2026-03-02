from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from .models import SMSMessage
from students.models import Student, StudentClass


@login_required
def send_sms(request):
    classes = StudentClass.objects.all()
    STATUS_CHOICES = [('', 'All Students'), ('active', 'Active'), ('inactive', 'Inactive'), ('graduated', 'Graduated')]

    if request.method == 'POST':
        class_id = request.POST.get('recipient_class') or None
        status_filter = request.POST.get('recipient_status', '')
        message_text = request.POST.get('message', '').strip()

        if not message_text:
            messages.error(request, 'Message cannot be empty.')
        else:
            qs = Student.objects.all()
            if class_id:
                qs = qs.filter(current_class_id=class_id)
            if status_filter:
                qs = qs.filter(status=status_filter)
            count = qs.count()

            # No gateway key — log only
            SMSMessage.objects.create(
                sent_by=request.user,
                recipient_class=StudentClass.objects.filter(pk=class_id).first() if class_id else None,
                recipient_status=status_filter,
                message=message_text,
                recipient_count=count,
                status='sent',
                gateway_response='[Log only — no SMS gateway configured]',
            )
            messages.success(request, f'SMS logged for {count} recipients. (No gateway configured — message saved to history.)')
            return redirect('sms_history')

    return render(request, 'sms/send_sms.html', {
        'classes': classes,
        'status_choices': STATUS_CHOICES,
    })


@login_required
def sms_history(request):
    sms_list = SMSMessage.objects.select_related('sent_by', 'recipient_class').all()
    total_sent = sms_list.aggregate(total=Count('id'))['total'] or 0
    total_recipients = sum(s.recipient_count for s in sms_list)
    return render(request, 'sms/sms_history.html', {
        'sms_list': sms_list,
        'total_sent': total_sent,
        'total_recipients': total_recipients,
    })
