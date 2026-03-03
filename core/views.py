from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from students.models import Student, AttendanceRecord
from staff.models import Teacher
from finance.models import Expense
from students.models import FeePayment
import json

@login_required
def index(request):
    user = request.user
    if getattr(user, 'role', None) and user.role.name.lower() == 'student':
        from django.shortcuts import redirect
        return redirect('student_dashboard')

    now = timezone.now()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # 1. Metric Cards
    total_students = Student.objects.filter(status='Active').count()
    total_teachers = Teacher.objects.filter(user__is_active=True).count()
    
    monthly_revenue = FeePayment.objects.filter(
        payment_date__gte=first_day_of_month
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    monthly_expenses = Expense.objects.filter(
        date__gte=first_day_of_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # 2. Charts (Chart.js)
    # 7-Day Attendance Trend
    attendance_labels = []
    attendance_data = []
    
    for i in range(6, -1, -1):
        target_date = (now - timedelta(days=i)).date()
        attendance_labels.append(target_date.strftime("%b %d"))
        
        # Calculate percentage for that day
        records = AttendanceRecord.objects.filter(session__date=target_date)
        total_records = records.count()
        present_count = records.filter(status='Present').count()
        
        if total_records > 0:
            percentage = round((present_count / total_records) * 100, 1)
        else:
            percentage = 0
            
        attendance_data.append(percentage)
        
    # 6-Month Income vs Expense
    months_labels = []
    income_data = []
    expense_data = []
    
    for i in range(5, -1, -1):
        target_month_date = now - timedelta(days=i*30) # Approximation
        target_month = target_month_date.month
        target_year = target_month_date.year
        months_labels.append(target_month_date.strftime("%b %Y"))
        
        inc = FeePayment.objects.filter(
            payment_date__year=target_year,
            payment_date__month=target_month
        ).aggregate(total=Sum('amount_paid'))['total'] or 0
        
        exp = Expense.objects.filter(
            date__year=target_year,
            date__month=target_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        income_data.append(float(inc))
        expense_data.append(float(exp))
        
    # 3. Recent Activity
    recent_payments = FeePayment.objects.filter().select_related('student__user', 'fee_type').order_by('-payment_date')[:5]

    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'monthly_revenue': monthly_revenue,
        'monthly_expenses': monthly_expenses,
        
        'attendance_labels': json.dumps(attendance_labels),
        'attendance_data': json.dumps(attendance_data),
        
        'months_labels': json.dumps(months_labels),
        'income_data': json.dumps(income_data),
        'expense_data': json.dumps(expense_data),
        
        'recent_payments': recent_payments,
    }
    return render(request, 'index.html', context)
