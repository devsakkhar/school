from students.models import InAppNotification

def notification_processor(request):
    if request.user.is_authenticated:
        unread = InAppNotification.objects.filter(user=request.user, is_read=False)[:5]
        unread_count = InAppNotification.objects.filter(user=request.user, is_read=False).count()
        return {
            'unread_notifications': unread,
            'unread_notifications_count': unread_count
        }
    return {}
