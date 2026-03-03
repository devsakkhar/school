from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from finance.models import Expense
from students.models import Student, AttendanceRecord, FeePayment
from online_exam.models import ExamAttempt
from django.contrib.auth import get_user_model
User = get_user_model()
from staff.models import LeaveRequest, Payroll
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta

@login_required
def financial_report(request):
    expenses = Expense.objects.all().order_by('-date')
    incomes = FeePayment.objects.filter(payment_status='Paid').order_by('-payment_date')
    
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    total_income = incomes.aggregate(total=Sum('amount_paid'))['total'] or 0
    
    context = {
        'expenses': expenses,
        'incomes': incomes,
        'total_expense': total_expense,
        'total_income': total_income,
        'net_balance': total_income - total_expense
    }
    return render(request, 'reports/financial_report.html', context)

@login_required
def attendance_report(request):
    # This report will show a class-wise attendance summary
    # Simply listing recent attendance records for now
    recent_attendance = AttendanceRecord.objects.select_related('student', 'session').order_by('-session__date')[:100]
    
    context = {
        'recent_attendance': recent_attendance
    }
    return render(request, 'reports/attendance_report.html', context)

@login_required
def academic_report(request):
    results = ExamAttempt.objects.select_related('student', 'exam').order_by('-started_at')[:100]
    
    context = {
        'results': results
    }
    return render(request, 'reports/academic_report.html', context)

@login_required
def staff_report(request):
    leave_requests = LeaveRequest.objects.select_related('applicant').order_by('-start_date')[:50]
    salaries = Payroll.objects.select_related('staff').order_by('-year', '-month')[:50]
    
    context = {
        'leave_requests': leave_requests,
        'salaries': salaries
    }
    return render(request, 'reports/staff_report.html', context)
