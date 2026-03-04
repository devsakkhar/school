from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import AdmissionCampaign, AdmissionApplication
from .forms import AdmissionApplicationForm

# ══════════════════════════════════════════════════════════
# Public Admission Form
# ══════════════════════════════════════════════════════════

def apply_admission(request):
    # Find active campaign
    today = timezone.now().date()
    campaign = AdmissionCampaign.objects.filter(is_active=True, start_date__lte=today, end_date__gte=today).first()
    
    if not campaign:
        return render(request, 'admissions/no_campaign.html')

    if request.method == 'POST':
        form = AdmissionApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.campaign = campaign
            application.save()
            return redirect('admission_success')
    else:
        form = AdmissionApplicationForm()

    return render(request, 'admissions/apply.html', {'form': form, 'campaign': campaign})

def admission_success(request):
    return render(request, 'admissions/success.html')

# ══════════════════════════════════════════════════════════
# Admin / Dashboard Views
# ══════════════════════════════════════════════════════════

@login_required
def admission_list(request):
    if request.user.role not in ['Admin', 'Principal']:
        messages.error(request, 'Access denied.')
        return redirect('index')
    
    applications = AdmissionApplication.objects.all().order_by('-application_date')
    return render(request, 'admissions/admin_list.html', {'applications': applications})

@login_required
def admission_detail(request, pk):
    if request.user.role not in ['Admin', 'Principal']:
        messages.error(request, 'Access denied.')
        return redirect('index')
    
    application = get_object_or_404(AdmissionApplication, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        remarks = request.POST.get('remarks', '')
        
        if action in ['Approved', 'Rejected']:
            application.status = action
            application.remarks = remarks
            application.save()
            
            if action == 'Approved':
                from accounts.models import CustomUser, Role
                from students.models import Student
                from django.contrib.auth.hashers import make_password
                
                # Check if user already exists
                username = f"std{application.pk}{application.first_name[:3].lower()}"
                if not CustomUser.objects.filter(username=username).exists():
                    student_role, _ = Role.objects.get_or_create(name='Student')
                    user = CustomUser.objects.create(
                        username=username,
                        password=make_password('school123'),
                        first_name=application.first_name,
                        last_name=application.last_name,
                        email=application.guardian_email,
                        role=student_role
                    )
                    
                    # Create student profile
                    Student.objects.create(
                        user=user,
                        current_class=application.applied_class,
                        name=f"{application.first_name} {application.last_name}",
                        father_name=application.father_name,
                        mother_name=application.mother_name,
                        date_of_birth=application.date_of_birth,
                        gender=application.gender,
                        blood_group=application.blood_group,
                        religion=application.religion,
                        phone=application.guardian_phone,
                        permanent_address=application.address,
                        present_address=application.address,
                        status='Active'
                    )
                    messages.success(request, f'Application Approved. Created Student with ID: {username}')
                else:
                    messages.success(request, 'Application Approved.')
            else:
                messages.warning(request, f'Application {action}.')
                
            return redirect('admission_list')
            
    return render(request, 'admissions/admin_detail.html', {'application': application})
