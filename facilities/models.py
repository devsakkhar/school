from django.db import models
from django.conf import settings
from students.models import Student

# ══════════════════════════════════════════════════════════
# Hostel Management
# ══════════════════════════════════════════════════════════

class Hostel(models.Model):
    HOSTEL_TYPES = [
        ('Boys', 'Boys'),
        ('Girls', 'Girls'),
        ('Co-ed', 'Co-ed'),
    ]
    name = models.CharField(max_length=150)
    hostel_type = models.CharField(max_length=20, choices=HOSTEL_TYPES)
    address = models.TextField()
    capacity = models.PositiveIntegerField(help_text="Total number of beds")
    manager_name = models.CharField(max_length=150)
    manager_phone = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.name} ({self.hostel_type})"

class Room(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=50)
    no_of_beds = models.PositiveIntegerField()
    cost_per_bed = models.DecimalField(max_digits=8, decimal_places=2)
    
    class Meta:
        unique_together = ('hostel', 'room_number')
        
    def __str__(self):
        return f"{self.hostel.name} - Room {self.room_number}"

class HostelAllocation(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='hostel_allocation')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='allocations')
    allocation_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Vacated', 'Vacated')], default='Active')
    
    def __str__(self):
        return f"{self.student} -> {self.room}"

# ══════════════════════════════════════════════════════════
# Transport Management
# ══════════════════════════════════════════════════════════

class Vehicle(models.Model):
    vehicle_number = models.CharField(max_length=50, unique=True)
    model = models.CharField(max_length=100)
    driver_name = models.CharField(max_length=150)
    driver_phone = models.CharField(max_length=20)
    max_seating_capacity = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.vehicle_number} ({self.model})"

class Route(models.Model):
    route_name = models.CharField(max_length=150)
    start_point = models.CharField(max_length=150)
    end_point = models.CharField(max_length=150)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, related_name='routes')
    monthly_fare = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __str__(self):
        return f"{self.route_name} (Cost: {self.monthly_fare})"

class TransportAllocation(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='transport_allocation')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='allocations')
    boarding_point = models.CharField(max_length=150)
    allocation_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Cancelled', 'Cancelled')], default='Active')
    
    def __str__(self):
        return f"{self.student} -> {self.route.route_name}"
