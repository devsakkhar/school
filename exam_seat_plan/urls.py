from django.urls import path
from . import views

urlpatterns = [
    # Exam Room Management
    path('rooms/', views.exam_room_list, name='exam_room_list'),
    path('rooms/create/', views.exam_room_create, name='exam_room_create'),
    path('rooms/<int:pk>/update/', views.exam_room_update, name='exam_room_update'),
    path('rooms/<int:pk>/delete/', views.exam_room_delete, name='exam_room_delete'),

    # Seat Plan Management
    path('exams/<int:pk>/seat-plan/', views.seat_plan_view, name='seat_plan_view'),
    path('exams/<int:pk>/seat-plan/generate/', views.seat_plan_generate, name='seat_plan_generate'),
]
