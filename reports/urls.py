from django.urls import path
from . import views

urlpatterns = [
    path('financial/', views.financial_report, name='financial_report'),
    path('attendance/', views.attendance_report, name='attendance_report'),
    path('academic/', views.academic_report, name='academic_report'),
    path('staff/', views.staff_report, name='staff_report'),
]
