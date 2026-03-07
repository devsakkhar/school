from django.urls import path
from . import views

urlpatterns = [
    # Hostel
    path('', views.hostel_list, name='hostel_list'),
    path('create/', views.hostel_create, name='hostel_create'),
    
    # Rooms
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/create/', views.room_create, name='room_create'),
    
    # Bed Allocations
    path('allocations/', views.allocation_list, name='allocation_list'),
    path('allocations/create/', views.allocation_create, name='allocation_create'),
    
    # Visitor Log
    path('visitors/', views.visitor_log_list, name='visitor_log_list'),
    path('visitors/create/', views.visitor_log_create, name='visitor_log_create'),
]
