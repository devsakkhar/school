from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from .models import Student, AttendanceSession, AttendanceRecord

@api_view(['POST'])
@permission_classes([AllowAny]) # In production, restrict by IP or Token
def api_attendance_punch(request):
    """
    Endpoint for RFID/Biometric hardware to send punch logs.
    Expected JSON: {"rfid_tag": "XYZ123"}
    """
    rfid_tag = request.data.get('rfid_tag')
    if not rfid_tag:
        return Response({'status': 'error', 'message': 'Missing rfid_tag'}, status=400)
        
    try:
        student = Student.objects.get(rfid_tag=rfid_tag, status='Active')
    except Student.DoesNotExist:
        return Response({'status': 'error', 'message': 'Student not found'}, status=404)
        
    today = timezone.now().date()
    current_time = timezone.now().time()
    
    # Get or create today's session for the student's class and section
    session, created = AttendanceSession.objects.get_or_create(
        student_class=student.current_class,
        section=student.section,
        date=today
    )
    
    # Get or create the student's attendance record
    record, r_created = AttendanceRecord.objects.get_or_create(
        session=session,
        student=student,
        defaults={'status': 'present'}
    )
    
    if r_created or not record.punch_in:
        record.punch_in = current_time
        record.status = 'present' # You could modify logic for 'late' based on school time
        record.save()
        return Response({'status': 'success', 'message': f'Punched IN for {student.user.get_full_name()}'})
    else:
        # Assuming second punch of the day is punch_out
        record.punch_out = current_time
        record.save()
        return Response({'status': 'success', 'message': f'Punched OUT for {student.user.get_full_name()}'})
