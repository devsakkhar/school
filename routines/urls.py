from django.urls import path
from . import views

urlpatterns = [
    # Class Routine
    path('class-routine/', views.class_routine_home, name='class_routine_home'),
    path('class-routine/create/', views.class_routine_create, name='class_routine_create'),
    path('class-routine/<int:pk>/edit/', views.class_routine_edit, name='class_routine_edit'),
    path('class-routine/<int:pk>/delete/', views.class_routine_delete, name='class_routine_delete'),

    # Exam Routine
    path('exam-routine/', views.exam_routine_home, name='exam_routine_home'),
    path('exam-routine/create/', views.exam_routine_create, name='exam_routine_create'),
    path('exam-routine/<int:pk>/edit/', views.exam_routine_edit, name='exam_routine_edit'),
    path('exam-routine/<int:pk>/delete/', views.exam_routine_delete, name='exam_routine_delete'),

    # Year Calendar
    path('calendar/', views.year_calendar, name='year_calendar'),
    path('calendar/create/', views.calendar_event_create, name='calendar_event_create'),
    path('calendar/<int:pk>/edit/', views.calendar_event_edit, name='calendar_event_edit'),
    path('calendar/<int:pk>/delete/', views.calendar_event_delete, name='calendar_event_delete'),

    # AJAX
    path('get-sections/', views.get_sections_ajax, name='routines_get_sections'),
]
