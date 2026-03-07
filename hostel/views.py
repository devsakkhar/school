from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Hostel, Room, BedAllocation, VisitorLog
from .forms import HostelForm, RoomForm, BedAllocationForm, VisitorLogForm

# ══════════════════════════════════════════════════════════
# Hostel Management
# ══════════════════════════════════════════════════════════
@login_required
def hostel_list(request):
    hostels = Hostel.objects.all().prefetch_related('rooms')
    return render(request, 'hostel/hostel_list.html', {'hostels': hostels})

@login_required
def hostel_create(request):
    if request.method == 'POST':
        form = HostelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hostel created successfully.')
            return redirect('hostel_list')
    else:
        form = HostelForm()
    return render(request, 'hostel/form.html', {'form': form, 'title': 'Add New Hostel', 'back_url': 'hostel_list'})

# ══════════════════════════════════════════════════════════
# Room Management
# ══════════════════════════════════════════════════════════
@login_required
def room_list(request):
    rooms = Room.objects.all().select_related('hostel')
    return render(request, 'hostel/room_list.html', {'rooms': rooms})

@login_required
def room_create(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room created successfully.')
            return redirect('room_list')
    else:
        form = RoomForm()
    return render(request, 'hostel/form.html', {'form': form, 'title': 'Add New Room', 'back_url': 'room_list'})

# ══════════════════════════════════════════════════════════
# Bed Allocation
# ══════════════════════════════════════════════════════════
@login_required
def allocation_list(request):
    allocations = BedAllocation.objects.all().select_related('student__user', 'room__hostel')
    return render(request, 'hostel/allocation_list.html', {'allocations': allocations})

@login_required
def allocation_create(request):
    if request.method == 'POST':
        form = BedAllocationForm(request.POST)
        if form.is_valid():
            room = form.cleaned_data['room']
            student = form.cleaned_data['student']
            if room.is_full():
                messages.error(request, f'{room} is already full.')
            elif BedAllocation.objects.filter(student=student, is_active=True).exists():
                messages.error(request, 'Student is already allocated a bed.')
            else:
                form.save()
                messages.success(request, 'Bed allocated successfully.')
                return redirect('allocation_list')
    else:
        form = BedAllocationForm()
    return render(request, 'hostel/form.html', {'form': form, 'title': 'Allocate Bed', 'back_url': 'allocation_list'})

# ══════════════════════════════════════════════════════════
# Visitor Log
# ══════════════════════════════════════════════════════════
@login_required
def visitor_log_list(request):
    logs = VisitorLog.objects.all().select_related('student__user').order_by('-visit_date', '-in_time')
    return render(request, 'hostel/visitor_log_list.html', {'logs': logs})

@login_required
def visitor_log_create(request):
    if request.method == 'POST':
        form = VisitorLogForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Visitor Log added.')
            return redirect('visitor_log_list')
    else:
        form = VisitorLogForm()
    return render(request, 'hostel/form.html', {'form': form, 'title': 'Add Visitor Log', 'back_url': 'visitor_log_list'})
