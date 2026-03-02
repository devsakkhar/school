from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Sum
from .models import Teacher, LeaveRequest, Payroll
from django.contrib.auth import get_user_model

User = get_user_model()

# ══════════════════════════════════════════════════════════
# Teacher Management
# ══════════════════════════════════════════════════════════
@login_required
def teacher_list(request):
    teachers = Teacher.objects.select_related('user').all()
    return render(request, 'staff/teacher_list.html', {'teachers': teachers})

@login_required
def teacher_create(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        
        # Ensure role is Teacher
        if not user.role or user.role.name != 'Teacher':
            user.role = 'Teacher'
            user.save()

        Teacher.objects.create(
            user=user,
            qualification=request.POST.get('qualification'),
            join_date=request.POST.get('join_date') or None,
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            basic_salary=request.POST.get('basic_salary') or 0.00
        )
        messages.success(request, 'Teacher profile created.')
        return redirect('teacher_list')
    
    # Only users who are not already in Teacher profile
    users = User.objects.exclude(id__in=Teacher.objects.values_list('user_id', flat=True))
    return render(request, 'staff/teacher_form.html', {'users': users, 'action': 'Add'})

@login_required
def teacher_edit(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == 'POST':
        teacher.qualification = request.POST.get('qualification')
        teacher.join_date = request.POST.get('join_date') or None
        teacher.phone = request.POST.get('phone')
        teacher.address = request.POST.get('address')
        teacher.basic_salary = request.POST.get('basic_salary') or 0.00
        teacher.save()
        messages.success(request, 'Teacher profile updated.')
        return redirect('teacher_list')
    return render(request, 'staff/teacher_form.html', {'teacher': teacher, 'action': 'Edit'})


# ══════════════════════════════════════════════════════════
# Leave Management
# ══════════════════════════════════════════════════════════
@login_required
def leave_list(request):
    if request.user.is_staff or (request.user.role and request.user.role.name in ['Admin', 'Principal']):
        # Admin can see all and approve
        leaves = LeaveRequest.objects.select_related('applicant').all().order_by('-applied_on')
    else:
        # Others see only their own
        leaves = LeaveRequest.objects.filter(applicant=request.user).order_by('-applied_on')
    return render(request, 'staff/leave_list.html', {'leaves': leaves})

@login_required
def leave_apply(request):
    if request.method == 'POST':
        LeaveRequest.objects.create(
            applicant=request.user,
            leave_type=request.POST.get('leave_type'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            reason=request.POST.get('reason'),
            status='Pending'
        )
        messages.success(request, 'Leave request submitted successfully.')
        return redirect('leave_list')
    leave_types = LeaveRequest.LEAVE_TYPES
    return render(request, 'staff/leave_form.html', {'leave_types': leave_types})

@login_required
def leave_approve(request, pk):
    if not (request.user.is_staff or (request.user.role and request.user.role.name in ['Admin', 'Principal'])):
        messages.error(request, 'You do not have permission to review leaves.')
        return redirect('leave_list')
    
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        remarks = request.POST.get('review_remarks', '')
        if status in ['Approved', 'Rejected']:
            leave.status = status
            leave.reviewed_by = request.user
            leave.review_remarks = remarks
            leave.save()
            messages.success(request, f'Leave request {status.lower()}.')
        return redirect('leave_list')
    return render(request, 'staff/leave_approve.html', {'leave': leave})


# ══════════════════════════════════════════════════════════
# Payroll
# ══════════════════════════════════════════════════════════
@login_required
def payroll_list(request):
    if request.user.is_staff or (request.user.role and request.user.role.name in ['Admin', 'Principal']):
        payrolls = Payroll.objects.select_related('staff').all().order_by('-year', '-month')
    else:
        payrolls = Payroll.objects.filter(staff=request.user).order_by('-year', '-month')
    return render(request, 'staff/payroll_list.html', {'payrolls': payrolls})

@login_required
def payroll_generate(request):
    if not (request.user.is_staff or (request.user.role and request.user.role.name in ['Admin', 'Principal'])):
        messages.error(request, 'You do not have permission.')
        return redirect('payroll_list')
    
    teachers = Teacher.objects.select_related('user')
    if request.method == 'POST':
        month = request.POST.get('month')
        year = request.POST.get('year')
        teacher_ids = request.POST.getlist('teacher_ids')
        
        count = 0
        for tid in teacher_ids:
            teacher = Teacher.objects.get(pk=tid)
            # prevent duplicate
            if not Payroll.objects.filter(staff=teacher.user, month=month, year=year).exists():
                allowances = request.POST.get(f'allowance_{tid}', 0)
                deductions = request.POST.get(f'deduction_{tid}', 0)
                Payroll.objects.create(
                    staff=teacher.user,
                    month=month,
                    year=year,
                    basic_salary=teacher.basic_salary,
                    allowances=allowances or 0,
                    deductions=deductions or 0
                )
                count += 1
        messages.success(request, f'Payroll generated for {count} staff.')
        return redirect('payroll_list')
    
    return render(request, 'staff/payroll_generate.html', {'teachers': teachers})

@login_required
def payroll_payslip(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    if not (request.user.is_staff or request.user == payroll.staff):
        return redirect('payroll_list')
    
    from accounts.models import SiteConfiguration
    config = SiteConfiguration.get_solo()
    return render(request, 'staff/payroll_payslip.html', {'payroll': payroll, 'config': config})
