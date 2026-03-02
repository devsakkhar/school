from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import transaction

from .models import ExamRoom, SeatAllocation
from students.models import Exam, Student
from .forms import ExamRoomForm, GenerateSeatPlanForm

@login_required
@permission_required('accounts.manage_academic_settings', raise_exception=True)
def exam_room_list(request):
    rooms = ExamRoom.objects.all()
    return render(request, 'exam_seat_plan/exam_room_list.html', {'rooms': rooms})

@login_required
@permission_required('accounts.manage_academic_settings', raise_exception=True)
def exam_room_create(request):
    if request.method == 'POST':
        form = ExamRoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam Room created successfully.')
            return redirect('exam_room_list')
    else:
        form = ExamRoomForm()
    return render(request, 'exam_seat_plan/exam_room_form.html', {'form': form, 'action': 'Create'})

@login_required
@permission_required('accounts.manage_academic_settings', raise_exception=True)
def exam_room_update(request, pk):
    room = get_object_or_404(ExamRoom, pk=pk)
    if request.method == 'POST':
        form = ExamRoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam Room updated successfully.')
            return redirect('exam_room_list')
    else:
        form = ExamRoomForm(instance=room)
    return render(request, 'exam_seat_plan/exam_room_form.html', {'form': form, 'action': 'Update'})

@login_required
@permission_required('accounts.manage_academic_settings', raise_exception=True)
def exam_room_delete(request, pk):
    room = get_object_or_404(ExamRoom, pk=pk)
    if request.method == 'POST':
        room.delete()
        messages.success(request, 'Exam Room deleted successfully.')
        return redirect('exam_room_list')
    return render(request, 'exam_seat_plan/exam_room_confirm_delete.html', {'room': room})

@login_required
@permission_required('accounts.manage_academic_settings', raise_exception=True)
def seat_plan_view(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    allocations = SeatAllocation.objects.filter(exam=exam).select_related('student', 'room')
    
    # Check if there are allocations, otherwise redirect to generate
    if not allocations.exists():
        messages.info(request, "No seat plan exists for this exam yet. Please generate one.")
        return redirect('seat_plan_generate', pk=exam.pk)

    # Group allocations by room
    rooms_data = {}
    for alloc in allocations:
        if alloc.room not in rooms_data:
            rooms_data[alloc.room] = []
        rooms_data[alloc.room].append(alloc)
        
    context = {
        'exam': exam,
        'rooms_data': rooms_data
    }
    return render(request, 'exam_seat_plan/seat_plan.html', context)

@login_required
@permission_required('accounts.manage_academic_settings', raise_exception=True)
def seat_plan_generate(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    
    # Get students for the class/section of this exam
    students = Student.objects.filter(current_class=exam.student_class, status='Active')
    if exam.section:
        students = students.filter(section=exam.section)
        
    students = list(students.order_by('roll_number'))
    
    if request.method == 'POST':
        form = GenerateSeatPlanForm(request.POST)
        if form.is_valid():
            selected_rooms = form.cleaned_data['rooms']
            total_capacity = sum(room.capacity for room in selected_rooms)
            
            if total_capacity < len(students):
                messages.error(request, f"Total capacity of selected rooms ({total_capacity}) is less than the number of students ({len(students)}). Please select more rooms.")
            else:
                try:
                    with transaction.atomic():
                        # Clear existing allocations for this exam
                        SeatAllocation.objects.filter(exam=exam).delete()
                        
                        student_idx = 0
                        allocations_to_create = []
                        
                        # Distribute students sequentially into rooms based on capacity
                        for room in selected_rooms:
                            room_count = 0
                            while room_count < room.capacity and student_idx < len(students):
                                student = students[student_idx]
                                # Format seat number (e.g. "Seat-1", "Seat-2", etc.)
                                seat_number = f"Seat-{room_count + 1}"
                                
                                allocations_to_create.append(
                                    SeatAllocation(
                                        exam=exam,
                                        student=student,
                                        room=room,
                                        seat_number=seat_number
                                    )
                                )
                                student_idx += 1
                                room_count += 1
                                
                        SeatAllocation.objects.bulk_create(allocations_to_create)
                        messages.success(request, f"Successfully generated seat plan for {len(allocations_to_create)} students across {len(selected_rooms)} rooms.")
                        return redirect('seat_plan_view', pk=exam.pk)
                except Exception as e:
                    messages.error(request, f"Error generating seat plan: {str(e)}")
    else:
        form = GenerateSeatPlanForm()
        
    context = {
        'exam': exam,
        'form': form,
        'student_count': len(students),
        'existing_plan': SeatAllocation.objects.filter(exam=exam).exists()
    }
    return render(request, 'exam_seat_plan/seat_plan_generate.html', context)
