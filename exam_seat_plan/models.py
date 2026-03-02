from django.db import models
from students.models import Exam, Student

class ExamRoom(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Room Name or Number (e.g., Room 101)")
    capacity = models.PositiveIntegerField(help_text="Maximum number of students this room can hold for an exam")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} (Capacity: {self.capacity})"

    class Meta:
        ordering = ['name']

class SeatAllocation(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='seat_allocations')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='allocated_seats')
    room = models.ForeignKey(ExamRoom, on_delete=models.CASCADE, related_name='allocations')
    seat_number = models.CharField(max_length=20, blank=True, null=True, help_text="Specific seat designation (optional)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('exam', 'student')
        ordering = ['room', 'seat_number', 'student']

    def __str__(self):
        return f"{self.student} -> {self.room} ({self.exam})"
