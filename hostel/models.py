from django.db import models
from django.conf import settings
from students.models import Student

class Hostel(models.Model):
    TYPE_CHOICES = [
        ('Boys', 'Boys'),
        ('Girls', 'Girls'),
        ('Co-ed', 'Co-ed'),
    ]
    name = models.CharField(max_length=150, unique=True)
    hostel_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Boys')
    capacity = models.PositiveIntegerField(default=0)
    warden = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='warden_of')
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.hostel_type})"

class Room(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(default=1)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('hostel', 'room_number')

    def current_occupants(self):
        return self.allocations.filter(is_active=True).count()

    def is_full(self):
        return self.current_occupants() >= self.capacity

    def __str__(self):
        return f"Room {self.room_number} - {self.hostel.name}"

class BedAllocation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='hostel_allocations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='allocations')
    allocation_date = models.DateField(auto_now_add=True)
    vacate_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} in {self.room}"

class VisitorLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='visitors')
    visitor_name = models.CharField(max_length=150)
    relation = models.CharField(max_length=50)
    visit_date = models.DateField(auto_now_add=True)
    in_time = models.TimeField()
    out_time = models.TimeField(null=True, blank=True)
    purpose = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.visitor_name} visited {self.student.user.get_full_name()} on {self.visit_date}"
