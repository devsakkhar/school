from django.urls import path
from . import views

urlpatterns = [
    # Hostel App
    path('hostels/', views.hostel_list, name='hostel_list'),
    path('hostels/<int:pk>/edit/', views.hostel_update, name='hostel_update'),
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/<int:pk>/edit/', views.room_update, name='room_update'),
    path('hostel-allocations/', views.hostel_allocation_list, name='hostel_allocation_list'),
    
    # Transport App
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/<int:pk>/edit/', views.vehicle_update, name='vehicle_update'),
    path('routes/', views.route_list, name='route_list'),
    path('routes/<int:pk>/edit/', views.route_update, name='route_update'),
    path('transport-allocations/', views.transport_allocation_list, name='transport_allocation_list'),
]
