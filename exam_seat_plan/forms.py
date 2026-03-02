from django import forms
from .models import ExamRoom
from students.models import Exam

class ExamRoomForm(forms.ModelForm):
    class Meta:
        model = ExamRoom
        fields = ['name', 'capacity', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Room 101'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 40'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional details'}),
        }

class GenerateSeatPlanForm(forms.Form):
    rooms = forms.ModelMultipleChoiceField(
        queryset=ExamRoom.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Rooms for Seat Plan"
    )
