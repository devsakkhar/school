from django import forms
from .models import Hostel, Room, HostelAllocation, Vehicle, Route, TransportAllocation

class HostelForm(forms.ModelForm):
    class Meta:
        model = Hostel
        fields = ['name', 'hostel_type', 'address', 'capacity', 'manager_name', 'manager_phone']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'hostel_type': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'manager_name': forms.TextInput(attrs={'class': 'form-control'}),
            'manager_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['hostel', 'room_number', 'no_of_beds', 'cost_per_bed']
        widgets = {
            'hostel': forms.Select(attrs={'class': 'form-select'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'no_of_beds': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost_per_bed': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['vehicle_number', 'model', 'driver_name', 'driver_phone', 'max_seating_capacity']
        widgets = {
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'driver_name': forms.TextInput(attrs={'class': 'form-control'}),
            'driver_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'max_seating_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['route_name', 'start_point', 'end_point', 'vehicle', 'monthly_fare']
        widgets = {
            'route_name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_point': forms.TextInput(attrs={'class': 'form-control'}),
            'end_point': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'monthly_fare': forms.NumberInput(attrs={'class': 'form-control'}),
        }
