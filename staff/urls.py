from django.urls import path
from . import views

urlpatterns = [
    # Teacher Management
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/add/', views.teacher_create, name='teacher_create'),
    path('teachers/<int:pk>/edit/', views.teacher_edit, name='teacher_edit'),
    
    # Leave Management
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/apply/', views.leave_apply, name='leave_apply'),
    path('leaves/<int:pk>/approve/', views.leave_approve, name='leave_approve'),

    # Payroll
    path('payroll/', views.payroll_list, name='payroll_list'),
    path('payroll/generate/', views.payroll_generate, name='payroll_generate'),
    path('payroll/<int:pk>/payslip/', views.payroll_payslip, name='payroll_payslip'),
]
