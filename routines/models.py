from django.db import models
from students.models import StudentClass, StudentSection


class ClassRoutine(models.Model):
    DAY_CHOICES = [
        ('saturday', 'Saturday'), ('sunday', 'Sunday'), ('monday', 'Monday'),
        ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'),
        ('friday', 'Friday'),
    ]

    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='routines')
    section = models.ForeignKey(StudentSection, on_delete=models.SET_NULL, null=True, blank=True)
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    period_number = models.PositiveIntegerField()
    subject_name = models.CharField(max_length=100)
    teacher_name = models.CharField(max_length=100, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.student_class} | {self.day} | Period {self.period_number} | {self.subject_name}"

    class Meta:
        ordering = ['student_class', 'day', 'period_number']
        unique_together = ('student_class', 'section', 'day', 'period_number')


class ExamRoutineEntry(models.Model):
    exam_name = models.CharField(max_length=200)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='exam_routines')
    section = models.ForeignKey(StudentSection, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=100)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)
    academic_year = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.exam_name} | {self.student_class} | {self.subject} | {self.exam_date}"

    class Meta:
        ordering = ['exam_date', 'start_time']


class CalendarEvent(models.Model):
    EVENT_TYPES = [
        ('holiday', 'Holiday'),
        ('exam', 'Exam'),
        ('activity', 'Activity'),
        ('meeting', 'Meeting'),
        ('result', 'Result Day'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='other')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    applies_to_all = models.BooleanField(default=True)
    student_class = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.start_date})"

    class Meta:
        ordering = ['start_date']
