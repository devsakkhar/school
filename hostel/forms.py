from django import forms
from .models import Hostel, Room, BedAllocation, VisitorLog

class HostelForm(forms.ModelForm):
    class Meta:
        model = Hostel
        fields = ['name', 'hostel_type', 'capacity', 'warden', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'hostel_type': forms.Select(attrs={'class': 'form-select'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'warden': forms.Select(attrs={'class': 'form-select select2'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['hostel', 'room_number', 'capacity', 'monthly_fee', 'description']
        widgets = {
            'hostel': forms.Select(attrs={'class': 'form-select select2'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'monthly_fee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class BedAllocationForm(forms.ModelForm):
    class Meta:
        model = BedAllocation
        fields = ['student', 'room', 'is_active']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select select2'}),
            'room': forms.Select(attrs={'class': 'form-select select2'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class VisitorLogForm(forms.ModelForm):
    class Meta:
        model = VisitorLog
        fields = ['student', 'visitor_name', 'relation', 'in_time', 'out_time', 'purpose']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select select2'}),
            'visitor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'relation': forms.TextInput(attrs={'class': 'form-control'}),
            'in_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'out_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
