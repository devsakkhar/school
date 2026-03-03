from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Hostel, Room, HostelAllocation, Vehicle, Route, TransportAllocation
from students.models import Student
from .forms import HostelForm, RoomForm, VehicleForm, RouteForm

# ══════════════════════════════════════════════════════════
# Hostel Views
# ══════════════════════════════════════════════════════════

@login_required
def hostel_list(request):
    hostels = Hostel.objects.all()
    if request.method == 'POST':
        form = HostelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hostel added successfully.')
            return redirect('hostel_list')
    else:
        form = HostelForm()
    
    return render(request, 'facilities/hostel_list.html', {'hostels': hostels, 'form': form})

@login_required
def hostel_update(request, pk):
    hostel = get_object_or_404(Hostel, pk=pk)
    if request.method == 'POST':
        form = HostelForm(request.POST, instance=hostel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hostel updated successfully.')
            return redirect('hostel_list')
    else:
        form = HostelForm(instance=hostel)
    return render(request, 'facilities/hostel_form.html', {'form': form, 'obj': hostel, 'title': 'Edit Hostel'})

@login_required
def room_list(request):
    rooms = Room.objects.all()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room added successfully.')
            return redirect('room_list')
    else:
        form = RoomForm()
    return render(request, 'facilities/room_list.html', {'rooms': rooms, 'form': form})

@login_required
def room_update(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room updated successfully.')
            return redirect('room_list')
    else:
        form = RoomForm(instance=room)
    return render(request, 'facilities/room_form.html', {'form': form, 'obj': room, 'title': 'Edit Room'})


@login_required
def hostel_allocation_list(request):
    allocations = HostelAllocation.objects.all().select_related('student', 'room')
    return render(request, 'facilities/hostel_allocation.html', {'allocations': allocations})

# ══════════════════════════════════════════════════════════
# Transport Views
# ══════════════════════════════════════════════════════════

@login_required
def vehicle_list(request):
    vehicles = Vehicle.objects.all()
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle added successfully.')
            return redirect('vehicle_list')
    else:
        form = VehicleForm()
    return render(request, 'facilities/vehicle_list.html', {'vehicles': vehicles, 'form': form})

@login_required
def vehicle_update(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle updated successfully.')
            return redirect('vehicle_list')
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'facilities/vehicle_form.html', {'form': form, 'obj': vehicle, 'title': 'Edit Vehicle'})


@login_required
def route_list(request):
    routes = Route.objects.all()
    if request.method == 'POST':
        form = RouteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Route added successfully.')
            return redirect('route_list')
    else:
        form = RouteForm()
    return render(request, 'facilities/route_list.html', {'routes': routes, 'form': form})

@login_required
def route_update(request, pk):
    route = get_object_or_404(Route, pk=pk)
    if request.method == 'POST':
        form = RouteForm(request.POST, instance=route)
        if form.is_valid():
            form.save()
            messages.success(request, 'Route updated successfully.')
            return redirect('route_list')
    else:
        form = RouteForm(instance=route)
    return render(request, 'facilities/route_form.html', {'form': form, 'obj': route, 'title': 'Edit Route'})


@login_required
def transport_allocation_list(request):
    allocations = TransportAllocation.objects.all().select_related('student', 'route')
    return render(request, 'facilities/transport_allocation.html', {'allocations': allocations})
