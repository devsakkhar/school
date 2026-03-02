from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import date, timedelta
import csv
import io

from .models import (
    Student, StudentClass, StudentSection,
    SchoolSettings, PromotionLog,
    StudentRemark, StudentDocument, ParentContactLog,
    AttendanceSession, AttendanceRecord,
    FeeType, FeePayment,
    Exam, StudentResult,
    BulkNotification,
)
from .forms import (
    StudentCreationForm, StudentChangeForm,
    SchoolSettingsForm, StudentClassForm, StudentSectionForm,
)

CustomUser = get_user_model()
from .models import ClassTeacher, Homework, HomeworkSubmission, Subject


@login_required
def student_list(request):
    search_query = request.GET.get('q', '')
    class_id = request.GET.get('class_id', '')
    section_id = request.GET.get('section_id', '')
    status_val = request.GET.get('status', '')
    
    students = Student.objects.all().order_by('-admission_date')
    
    if search_query:
        students = students.filter(
            Q(admission_number__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(current_class__name__icontains=search_query)
        )
        
    if class_id:
        students = students.filter(current_class_id=class_id)
        
    if section_id:
        students = students.filter(section_id=section_id)
        
    if status_val:
        students = students.filter(status=status_val)
        
    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'students': page_obj, 
        'search_query': search_query,
        'class_id': class_id,
        'section_id': section_id,
        'status_val': status_val,
        'classes': StudentClass.objects.all().order_by('name'),
        'status_choices': Student.STATUS_CHOICES
    }
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'students/partials/student_table.html', context)
        
    return render(request, 'students/student_list.html', context)

@login_required
# @permission_required('students.add_student', raise_exception=True)
def student_create(request):
    if request.method == 'POST':
        form = StudentCreationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Student created successfully!')
                return redirect('student_list')
            except Exception as e:
                messages.error(request, f"Error creating student: {e}")
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Auto-generate admission number and roll number
        import datetime
        current_year = datetime.datetime.now().year
        students_this_year = Student.objects.filter(admission_date__year=current_year).count()
        new_admission_number = f"ADM{current_year}{(students_this_year + 1):04d}"
        
        # Calculate next roll number based on total students (simple increment)
        # Note: In a real scenario, roll number is usually per class/section.
        total_students = Student.objects.count()
        new_roll_number = str(total_students + 1)
        
        form = StudentCreationForm(initial={
            'admission_number': new_admission_number,
            'roll_number': new_roll_number,
            'admission_date': datetime.datetime.now().date()
        })
        
    return render(request, 'students/student_form.html', {'form': form, 'action': 'Create'})

@login_required
# @permission_required('students.change_student', raise_exception=True)
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentChangeForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Student updated successfully!')
                return redirect('student_list')
            except Exception as e:
                messages.error(request, f"Error updating student: {e}")
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentChangeForm(instance=student)
        
    return render(request, 'students/student_form.html', {'form': form, 'action': 'Update'})

@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'students/student_detail.html', {'student': student})

@login_required
# @permission_required('students.delete_student', raise_exception=True)
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        user = student.user
        student.delete()
        user.delete() # Also delete the associated user account
        messages.success(request, 'Student deleted successfully!')
        return redirect('student_list')
        
    return render(request, 'students/student_confirm_delete.html', {'student': student})

@login_required
def get_sections(request):
    class_id = request.GET.get('class_id')
    if class_id:
        sections = StudentSection.objects.filter(student_class_id=class_id)
        sections_data = []
        for section in sections:
            sections_data.append({'id': section.id, 'name': section.name})
        return JsonResponse(sections_data, safe=False)
    return JsonResponse([], safe=False)

@login_required
def student_export_csv(request):
    search_query = request.GET.get('q', '')
    class_id = request.GET.get('class_id', '')
    section_id = request.GET.get('section_id', '')
    status_val = request.GET.get('status', '')
    
    students = Student.objects.all().order_by('-admission_date')
    
    if search_query:
        students = students.filter(
            Q(admission_number__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(current_class__name__icontains=search_query)
        )
        
    if class_id:
        students = students.filter(current_class_id=class_id)
        
    if section_id:
        students = students.filter(section_id=section_id)
        
    if status_val:
        students = students.filter(status=status_val)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Admission Number', 'First Name', 'Last Name', 'Email', 
        'Class', 'Section', 'Roll Number', 'Status', 'Phone Number', 
        'Father Name', 'Mother Name', 'Present Address'
    ])

    for student in students:
        s_class = student.current_class.name if student.current_class else 'N/A'
        s_section = student.section.name if student.section else 'N/A'
        writer.writerow([
            student.admission_number,
            student.user.first_name,
            student.user.last_name,
            student.user.email,
            s_class,
            s_section,
            student.roll_number,
            student.status,
            student.phone_number,
            student.father_name,
            student.mother_name,
            student.present_address
        ])

    return response

@login_required
def generate_id_cards(request):
    search_query = request.GET.get('q', '')
    class_id = request.GET.get('class_id', '')
    section_id = request.GET.get('section_id', '')
    status_val = request.GET.get('status', '')
    student_id = request.GET.get('student_id', '')
    
    school_settings = SchoolSettings.objects.first()
    
    # We don't paginate ID cards so we can print all selected at once
    students = Student.objects.all().order_by('current_class', 'section', 'roll_number')
    
    if student_id:
        students = students.filter(id=student_id)
    else:
        if search_query:
            students = students.filter(
                Q(admission_number__icontains=search_query) |
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(current_class__name__icontains=search_query)
            )
            
        if class_id:
            students = students.filter(current_class_id=class_id)
            
        if section_id:
            students = students.filter(section_id=section_id)
            
        if status_val:
            students = students.filter(status=status_val)

    context = {
        'students': students,
        'school': school_settings
    }
    return render(request, 'students/id_card_template.html', context)

@login_required
def class_promotion(request):
    classes = StudentClass.objects.all().order_by('name')
    students = []
    from_class_id = request.GET.get('from_class')
    
    if from_class_id:
        # Only show active students for promotion
        students = Student.objects.filter(current_class_id=from_class_id, status='Active').order_by('section__name', 'roll_number')
        
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'promote':
            student_ids = request.POST.getlist('student_ids')
            to_class_id = request.POST.get('to_class')
            to_section_id = request.POST.get('to_section')
            
            if not student_ids:
                messages.error(request, "No students selected for promotion.")
            elif not to_class_id:
                messages.error(request, "Please select a target class.")
            else:
                try:
                    to_class = StudentClass.objects.get(id=to_class_id)
                    to_section = StudentSection.objects.get(id=to_section_id) if to_section_id else None
                    
                    # Perform bulk update
                    updated_count = Student.objects.filter(id__in=student_ids).update(
                        current_class=to_class,
                        section=to_section
                    )
                    # Record the promotion in the log
                    PromotionLog.objects.create(
                        promoted_by=request.user,
                        from_class=StudentClass.objects.get(id=from_class_id) if from_class_id else None,
                        to_class=to_class,
                        to_section=to_section,
                        student_count=updated_count
                    )
                    messages.success(request, f"Successfully promoted {updated_count} students to {to_class.name}.")
                    return redirect('class_promotion')
                except Exception as e:
                    messages.error(request, f"An error occurred: {str(e)}")
                    
    promotion_logs = PromotionLog.objects.select_related('from_class', 'to_class', 'to_section', 'promoted_by').all()[:20]
    
    context = {
        'classes': classes,
        'students': students,
        'from_class_id': from_class_id,
        'promotion_logs': promotion_logs,
    }
    return render(request, 'students/class_promotion.html', context)

@login_required
def school_settings_view(request):
    school, created = SchoolSettings.objects.get_or_create(id=1)
    
    if request.method == 'POST':
        form = SchoolSettingsForm(request.POST, request.FILES, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, 'School settings updated successfully.')
            return redirect('school_settings')
    else:
        form = SchoolSettingsForm(instance=school)
        
    return render(request, 'students/school_settings.html', {'form': form, 'school': school})

@login_required
# @permission_required('students.add_student', raise_exception=True)
def student_bulk_upload(request):
    if request.method == 'POST':
        if 'csv_file' not in request.FILES:
            messages.error(request, 'Please select a CSV file.')
            return redirect('student_bulk_upload')
            
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid CSV file.')
            return redirect('student_bulk_upload')
            
        try:
            student_group = Group.objects.get(name__iexact='Student')
        except Group.DoesNotExist:
            messages.error(request, 'Student role/group does not exist. Please run setup_roles command.')
            return redirect('student_bulk_upload')

        try:
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            success_count = 0
            error_count = 0
            
            for row in reader:
                try:
                    # Required fields
                    first_name = row.get('first_name', '').strip()
                    last_name = row.get('last_name', '').strip()
                    email = row.get('email', '').strip()
                    admission_number = row.get('admission_number', '').strip()
                    current_class_name = row.get('current_class', '').strip()
                    section_name = row.get('section', '').strip()
                    
                    if not all([first_name, last_name, email, admission_number, current_class_name]):
                        error_count += 1
                        continue # Skip invalid row
                        
                    # Check if user with email or admission number already exists
                    if CustomUser.objects.filter(email=email).exists() or Student.objects.filter(admission_number=admission_number).exists():
                        error_count += 1
                        continue
                        
                    # Get or create class
                    current_class_obj, _ = StudentClass.objects.get_or_create(name=current_class_name)
                    
                    # Get or create section if provided
                    section_obj = None
                    if section_name:
                        section_obj, _ = StudentSection.objects.get_or_create(name=section_name, student_class=current_class_obj)
                        
                    # Create User
                    user = CustomUser.objects.create_user(
                        username=admission_number,
                        email=email,
                        password='123456',
                        first_name=first_name,
                        last_name=last_name
                    )
                    user.role = student_group
                    user.save()
                    
                    # Create Student
                    student = Student(
                        user=user,
                        admission_number=admission_number,
                        current_class=current_class_obj,
                        section=section_obj,
                        
                        # Optional fields mapped carefully
                        gender=row.get('gender', ''),
                        blood_group=row.get('blood_group', ''),
                        religion=row.get('religion', ''),
                        phone_number=row.get('phone_number', ''),
                        present_address=row.get('present_address', ''),
                        guardian_name=row.get('guardian_name', ''),
                        guardian_phone=row.get('guardian_phone', '')
                    )
                    student.save()
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    print(f"Error processing row {row}: {e}")
                    
            if success_count > 0:
                messages.success(request, f'Successfully imported {success_count} students.')
            if error_count > 0:
                messages.warning(request, f'Failed to import {error_count} rows. Please check data format or duplicates.')
                
            return redirect('student_list')
            
        except Exception as e:
            messages.error(request, f'Error reading CSV file: {e}')
            
    return render(request, 'students/student_bulk_upload.html')

@login_required
def student_bulk_upload_template(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_bulk_upload_template.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['first_name', 'last_name', 'email', 'admission_number', 'current_class', 'gender', 'blood_group', 'religion', 'phone_number', 'present_address', 'guardian_name', 'guardian_phone'])
    writer.writerow(['John', 'Doe', 'john.doe@example.com', 'ADM2024001', 'Class 1', 'Male', 'O+', 'Islam', '1234567890', '123 Main St, City', 'Jane Doe', '0987654321'])
    writer.writerow(['Jane', 'Smith', 'jane.smith@example.com', 'ADM2024002', 'Class 2', 'Female', 'A+', 'Christianity', '9876543210', '456 Oak St, City', 'John Smith', '0123456789'])
    
    return response

# --- Class CRUD Views ---

@login_required
def class_list(request):
    classes = StudentClass.objects.all().order_by('name')
    return render(request, 'students/class_list.html', {'classes': classes})

@login_required
def class_create(request):
    if request.method == 'POST':
        form = StudentClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class created successfully!')
            return redirect('class_list')
    else:
        form = StudentClassForm()
    return render(request, 'students/class_form.html', {'form': form, 'action': 'Create'})

@login_required
def class_update(request, pk):
    obj = get_object_or_404(StudentClass, pk=pk)
    if request.method == 'POST':
        form = StudentClassForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class updated successfully!')
            return redirect('class_list')
    else:
        form = StudentClassForm(instance=obj)
    return render(request, 'students/class_form.html', {'form': form, 'action': 'Edit'})

@login_required
def class_delete(request, pk):
    obj = get_object_or_404(StudentClass, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Class deleted successfully!')
        return redirect('class_list')
    return render(request, 'students/class_confirm_delete.html', {'class_obj': obj})

# --- Section CRUD Views ---

@login_required
def section_list(request):
    sections = StudentSection.objects.all().order_by('student_class__name', 'name')
    return render(request, 'students/section_list.html', {'sections': sections})

@login_required
def section_create(request):
    if request.method == 'POST':
        form = StudentSectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Section created successfully!')
            return redirect('section_list')
    else:
        form = StudentSectionForm()
    return render(request, 'students/section_form.html', {'form': form, 'action': 'Create'})

@login_required
def section_update(request, pk):
    obj = get_object_or_404(StudentSection, pk=pk)
    if request.method == 'POST':
        form = StudentSectionForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Section updated successfully!')
            return redirect('section_list')
    else:
        form = StudentSectionForm(instance=obj)
    return render(request, 'students/section_form.html', {'form': form, 'action': 'Edit'})

@login_required
def section_delete(request, pk):
    obj = get_object_or_404(StudentSection, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Section deleted successfully!')
        return redirect('section_list')
    return render(request, 'students/section_confirm_delete.html', {'section_obj': obj})


# ══════════════════════════════════════════════════
# Student Remarks / Notes
# ══════════════════════════════════════════════════
@login_required
def student_remarks(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        note = request.POST.get('note', '').strip()
        if note:
            StudentRemark.objects.create(student=student, author=request.user, note=note)
            messages.success(request, 'Remark added.')
        return redirect('student_remarks', pk=pk)
    remarks = student.remarks.select_related('author').all()
    return render(request, 'students/student_remarks.html', {'student': student, 'remarks': remarks})

@login_required
def student_remark_delete(request, pk, remark_pk):
    remark = get_object_or_404(StudentRemark, pk=remark_pk, student__pk=pk)
    if request.method == 'POST':
        remark.delete()
        messages.success(request, 'Remark deleted.')
    return redirect('student_remarks', pk=pk)


# ══════════════════════════════════════════════════
# Student Documents
# ══════════════════════════════════════════════════
@login_required
def student_documents(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', 'other')
        f = request.FILES.get('file')
        if title and f:
            StudentDocument.objects.create(student=student, title=title, category=category, file=f, uploaded_by=request.user)
            messages.success(request, 'Document uploaded.')
        return redirect('student_documents', pk=pk)
    docs = student.documents.select_related('uploaded_by').all()
    categories = StudentDocument.CATEGORY_CHOICES
    return render(request, 'students/student_documents.html', {'student': student, 'docs': docs, 'categories': categories})

@login_required
def student_document_delete(request, pk, doc_pk):
    doc = get_object_or_404(StudentDocument, pk=doc_pk, student__pk=pk)
    if request.method == 'POST':
        doc.file.delete(save=False)
        doc.delete()
        messages.success(request, 'Document deleted.')
    return redirect('student_documents', pk=pk)


# ══════════════════════════════════════════════════
# Parent Contact Log
# ══════════════════════════════════════════════════
@login_required
def student_contacts(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        contact_date = request.POST.get('contact_date')
        method = request.POST.get('method', 'call')
        notes = request.POST.get('notes', '')
        if contact_date:
            ParentContactLog.objects.create(student=student, contacted_by=request.user, contact_date=contact_date, method=method, notes=notes)
            messages.success(request, 'Contact log added.')
        return redirect('student_contacts', pk=pk)
    logs = student.contact_logs.select_related('contacted_by').all()
    methods = ParentContactLog.METHOD_CHOICES
    return render(request, 'students/student_contacts.html', {'student': student, 'logs': logs, 'methods': methods, 'today': date.today().isoformat()})

@login_required
def student_contact_delete(request, pk, log_pk):
    log = get_object_or_404(ParentContactLog, pk=log_pk, student__pk=pk)
    if request.method == 'POST':
        log.delete()
        messages.success(request, 'Log deleted.')
    return redirect('student_contacts', pk=pk)


# ══════════════════════════════════════════════════
# Analytics Dashboard
# ══════════════════════════════════════════════════
@login_required
def student_analytics(request):
    total = Student.objects.count()
    active = Student.objects.filter(status='active').count()
    by_class = list(Student.objects.values('current_class__name').annotate(count=Count('id')).order_by('current_class__name'))
    by_status = list(Student.objects.values('status').annotate(count=Count('id')).order_by('status'))
    by_gender = list(Student.objects.values('gender').annotate(count=Count('id')).order_by('gender'))
    by_blood = list(Student.objects.values('blood_group').annotate(count=Count('id')).order_by('blood_group'))
    return render(request, 'students/analytics.html', {'total': total, 'active': active, 'by_class': by_class, 'by_status': by_status, 'by_gender': by_gender, 'by_blood': by_blood})

@login_required
def student_analytics_data(request):
    by_class = list(Student.objects.values('current_class__name').annotate(count=Count('id')).order_by('current_class__name'))
    by_status = list(Student.objects.values('status').annotate(count=Count('id')).order_by('status'))
    return JsonResponse({'by_class': by_class, 'by_status': by_status})


# ══════════════════════════════════════════════════
# Attendance
# ══════════════════════════════════════════════════
@login_required
def attendance_home(request):
    recent_sessions = AttendanceSession.objects.select_related('student_class', 'section').all()[:20]
    classes = StudentClass.objects.all()
    return render(request, 'students/attendance_home.html', {'recent_sessions': recent_sessions, 'classes': classes, 'today': date.today().isoformat()})

@login_required
def attendance_take(request):
    class_id = request.GET.get('class_id') or request.POST.get('class_id')
    section_id = request.GET.get('section_id') or request.POST.get('section_id')
    att_date = request.GET.get('date') or request.POST.get('date') or date.today().isoformat()
    classes = StudentClass.objects.all()
    sections = StudentSection.objects.filter(student_class_id=class_id) if class_id else []
    students = []
    session = None

    if class_id:
        students_qs = Student.objects.filter(current_class_id=class_id, status='active')
        if section_id:
            students_qs = students_qs.filter(section_id=section_id)
        students = students_qs.select_related('user')
        session_filter = {'student_class_id': class_id, 'date': att_date}
        if section_id:
            session_filter['section_id'] = section_id
        session = AttendanceSession.objects.filter(**session_filter).first()

    if request.method == 'POST' and class_id and students:
        student_class = get_object_or_404(StudentClass, pk=class_id)
        section = StudentSection.objects.filter(pk=section_id).first() if section_id else None
        session, created = AttendanceSession.objects.get_or_create(student_class=student_class, section=section, date=att_date, defaults={'recorded_by': request.user})
        for student in students:
            status = request.POST.get(f'status_{student.id}', 'absent')
            AttendanceRecord.objects.update_or_create(session=session, student=student, defaults={'status': status})
        messages.success(request, f'Attendance saved for {att_date}.')
        return redirect('attendance_home')

    existing_records = {}
    if session:
        for rec in session.records.all():
            existing_records[rec.student_id] = rec.status
    return render(request, 'students/attendance_take.html', {'classes': classes, 'sections': sections, 'students': students, 'class_id': class_id, 'section_id': section_id, 'att_date': att_date, 'existing_records': existing_records, 'session': session, 'status_choices': AttendanceRecord.STATUS_CHOICES})

@login_required
def attendance_report(request):
    class_id = request.GET.get('class_id')
    section_id = request.GET.get('section_id')
    start_date = request.GET.get('start_date', (date.today() - timedelta(days=30)).isoformat())
    end_date = request.GET.get('end_date', date.today().isoformat())
    classes = StudentClass.objects.all()
    sections = StudentSection.objects.filter(student_class_id=class_id) if class_id else []
    report_data = []
    if class_id:
        sessions = AttendanceSession.objects.filter(student_class_id=class_id, date__range=[start_date, end_date])
        if section_id:
            sessions = sessions.filter(section_id=section_id)
        session_ids = sessions.values_list('id', flat=True)
        total_sessions = sessions.count()
        students = Student.objects.filter(current_class_id=class_id, status='active')
        if section_id:
            students = students.filter(section_id=section_id)
        for student in students.select_related('user'):
            records = AttendanceRecord.objects.filter(session_id__in=session_ids, student=student)
            present = records.filter(status='present').count()
            absent = records.filter(status='absent').count()
            late = records.filter(status='late').count()
            pct = round((present / total_sessions * 100), 1) if total_sessions > 0 else 0
            report_data.append({'student': student, 'present': present, 'absent': absent, 'late': late, 'total': total_sessions, 'pct': pct, 'low': pct < 75})
    return render(request, 'students/attendance_report.html', {'classes': classes, 'sections': sections, 'report_data': report_data, 'class_id': class_id, 'section_id': section_id, 'start_date': start_date, 'end_date': end_date})


# ══════════════════════════════════════════════════
# Fee Management
# ══════════════════════════════════════════════════
@login_required
def fee_list(request):
    fee_types = FeeType.objects.select_related('applies_to_class').all()
    return render(request, 'students/fee_list.html', {'fee_types': fee_types})

@login_required
def fee_type_create(request):
    classes = StudentClass.objects.all()
    if request.method == 'POST':
        FeeType.objects.create(name=request.POST.get('name'), amount=request.POST.get('amount'), academic_year=request.POST.get('academic_year', ''), due_date=request.POST.get('due_date') or None, applies_to_class=StudentClass.objects.filter(pk=request.POST.get('applies_to_class')).first(), description=request.POST.get('description', ''))
        messages.success(request, 'Fee type created.')
        return redirect('fee_list')
    return render(request, 'students/fee_type_form.html', {'classes': classes, 'action': 'Create'})

@login_required
def fee_type_update(request, pk):
    fee_type = get_object_or_404(FeeType, pk=pk)
    classes = StudentClass.objects.all()
    if request.method == 'POST':
        fee_type.name = request.POST.get('name')
        fee_type.amount = request.POST.get('amount')
        fee_type.academic_year = request.POST.get('academic_year', '')
        fee_type.due_date = request.POST.get('due_date') or None
        fee_type.applies_to_class = StudentClass.objects.filter(pk=request.POST.get('applies_to_class')).first()
        fee_type.description = request.POST.get('description', '')
        fee_type.save()
        messages.success(request, 'Fee type updated.')
        return redirect('fee_list')
    return render(request, 'students/fee_type_form.html', {'fee_type': fee_type, 'classes': classes, 'action': 'Edit'})

@login_required
def fee_type_delete(request, pk):
    fee_type = get_object_or_404(FeeType, pk=pk)
    if request.method == 'POST':
        fee_type.delete()
        messages.success(request, 'Fee type deleted.')
        return redirect('fee_list')
    return render(request, 'students/fee_type_confirm_delete.html', {'fee_type': fee_type})

@login_required
def fee_payments(request):
    payments = FeePayment.objects.select_related('student__user', 'fee_type', 'received_by').all()
    class_id = request.GET.get('class_id')
    fee_type_id = request.GET.get('fee_type_id')
    if class_id:
        payments = payments.filter(student__current_class_id=class_id)
    if fee_type_id:
        payments = payments.filter(fee_type_id=fee_type_id)
    classes = StudentClass.objects.all()
    fee_types = FeeType.objects.all()
    total_collected = payments.aggregate(total=Sum('amount_paid'))['total'] or 0
    paginator = Paginator(payments, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'students/fee_payments.html', {'page_obj': page_obj, 'classes': classes, 'fee_types': fee_types, 'class_id': class_id, 'fee_type_id': fee_type_id, 'total_collected': total_collected})

@login_required
def record_payment(request):
    students = Student.objects.filter(status='active').select_related('user', 'current_class')
    fee_types = FeeType.objects.all()
    if request.method == 'POST':
        student = get_object_or_404(Student, pk=request.POST.get('student'))
        fee_type = get_object_or_404(FeeType, pk=request.POST.get('fee_type'))
        FeePayment.objects.create(student=student, fee_type=fee_type, amount_paid=request.POST.get('amount_paid'), payment_date=request.POST.get('payment_date') or date.today(), received_by=request.user, notes=request.POST.get('notes', ''))
        messages.success(request, f'Payment recorded for {student.user.get_full_name()}.')
        return redirect('fee_payments')
    return render(request, 'students/record_payment.html', {'students': students, 'fee_types': fee_types, 'today': date.today().isoformat()})

@login_required
def student_fee(request, pk):
    student = get_object_or_404(Student, pk=pk)
    payments = student.fee_payments.select_related('fee_type', 'received_by').all()
    total_paid = payments.aggregate(total=Sum('amount_paid'))['total'] or 0
    fee_types = FeeType.objects.filter(Q(applies_to_class=student.current_class) | Q(applies_to_class__isnull=True))
    return render(request, 'students/student_fee.html', {'student': student, 'payments': payments, 'total_paid': total_paid, 'fee_types': fee_types, 'today': date.today().isoformat()})


# ══════════════════════════════════════════════════
# Academic Results
# ══════════════════════════════════════════════════
@login_required
def exam_list(request):
    exams = Exam.objects.select_related('student_class', 'section', 'created_by').all()
    class_id = request.GET.get('class_id')
    if class_id:
        exams = exams.filter(student_class_id=class_id)
    classes = StudentClass.objects.all()
    return render(request, 'students/exam_list.html', {'exams': exams, 'classes': classes, 'class_id': class_id})

@login_required
def exam_create(request):
    classes = StudentClass.objects.all()
    if request.method == 'POST':
        class_obj = get_object_or_404(StudentClass, pk=request.POST.get('student_class'))
        section = StudentSection.objects.filter(pk=request.POST.get('section')).first()
        exam = Exam.objects.create(name=request.POST.get('name'), student_class=class_obj, section=section, exam_date=request.POST.get('exam_date'), total_marks=request.POST.get('total_marks', 100), pass_marks=request.POST.get('pass_marks', 33), academic_year=request.POST.get('academic_year', ''), created_by=request.user)
        students = Student.objects.filter(current_class=class_obj, status='active')
        if section:
            students = students.filter(section=section)
        StudentResult.objects.bulk_create([StudentResult(exam=exam, student=s) for s in students], ignore_conflicts=True)
        messages.success(request, f'Exam "{exam.name}" created with {students.count()} student slots.')
        return redirect('exam_results', pk=exam.pk)
    return render(request, 'students/exam_form.html', {'classes': classes, 'today': date.today().isoformat()})

@login_required
def exam_results(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    results = exam.results.select_related('student__user').order_by('student__user__first_name')
    if request.method == 'POST':
        for result in results:
            marks = request.POST.get(f'marks_{result.student_id}', '').strip()
            result.marks_obtained = marks if marks else None
            result.remarks = request.POST.get(f'remarks_{result.student_id}', '')
            result.save()
        messages.success(request, 'Results saved.')
        return redirect('exam_results', pk=pk)
    passed = results.filter(grade__in=['A+', 'A', 'B', 'C', 'D']).count()
    failed = results.filter(grade='F').count()
    return render(request, 'students/exam_results.html', {'exam': exam, 'results': results, 'passed': passed, 'failed': failed})

@login_required
def exam_delete(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        exam.delete()
        messages.success(request, 'Exam deleted.')
        return redirect('exam_list')
    return render(request, 'students/exam_confirm_delete.html', {'exam': exam})

@login_required
def student_report_card(request, pk):
    student = get_object_or_404(Student, pk=pk)
    results = student.results.select_related('exam').order_by('-exam__exam_date')
    return render(request, 'students/report_card.html', {'student': student, 'results': results})


# ══════════════════════════════════════════════════
# Bulk Notifications
# ══════════════════════════════════════════════════
@login_required
def notifications_list(request):
    notifications = BulkNotification.objects.select_related('sent_by', 'recipient_class').all()
    return render(request, 'students/notifications_list.html', {'notifications': notifications})

@login_required
def send_notification(request):
    classes = StudentClass.objects.all()
    if request.method == 'POST':
        class_id = request.POST.get('recipient_class') or None
        status_filter = request.POST.get('recipient_status', '')
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()
        if subject and message_text:
            qs = Student.objects.filter(status=status_filter) if status_filter else Student.objects.filter(status='active')
            if class_id:
                qs = qs.filter(current_class_id=class_id)
            count = qs.count()
            BulkNotification.objects.create(sent_by=request.user, recipient_class=StudentClass.objects.filter(pk=class_id).first() if class_id else None, recipient_status=status_filter, subject=subject, message=message_text, recipient_count=count)
            messages.success(request, f'Notification sent to {count} students.')
            return redirect('notifications_list')
    STATUS_CHOICES = [('', 'All'), ('active', 'Active'), ('inactive', 'Inactive'), ('graduated', 'Graduated')]
    return render(request, 'students/send_notification.html', {'classes': classes, 'status_choices': STATUS_CHOICES})


# ══════════════════════════════════════════════════════════
# Subject Management
# ══════════════════════════════════════════════════════════
from .models import Subject, ExamSubjectResult

@login_required
def subject_list(request):
    from .models import Subject
    class_id = request.GET.get('class_id')
    subjects = Subject.objects.select_related('student_class')
    if class_id:
        subjects = subjects.filter(student_class_id=class_id)
    classes = StudentClass.objects.all()
    return render(request, 'students/subject_list.html', {
        'subjects': subjects, 'classes': classes, 'class_id': class_id,
    })

@login_required
def subject_create(request):
    classes = StudentClass.objects.all()
    if request.method == 'POST':
        Subject.objects.create(
            name=request.POST.get('name'),
            code=request.POST.get('code', ''),
            student_class=StudentClass.objects.get(pk=request.POST.get('student_class')),
            teacher_name=request.POST.get('teacher_name', ''),
            description=request.POST.get('description', ''),
        )
        messages.success(request, 'Subject created.')
        return redirect('subject_list')
    return render(request, 'students/subject_form.html', {'classes': classes, 'action': 'Add'})

@login_required
def subject_edit(request, pk):
    from .models import Subject
    subject = get_object_or_404(Subject, pk=pk)
    classes = StudentClass.objects.all()
    if request.method == 'POST':
        subject.name = request.POST.get('name')
        subject.code = request.POST.get('code', '')
        subject.student_class = StudentClass.objects.get(pk=request.POST.get('student_class'))
        subject.teacher_name = request.POST.get('teacher_name', '')
        subject.description = request.POST.get('description', '')
        subject.save()
        messages.success(request, 'Subject updated.')
        return redirect('subject_list')
    return render(request, 'students/subject_form.html', {'subject': subject, 'classes': classes, 'action': 'Edit'})

@login_required
def subject_delete(request, pk):
    from .models import Subject
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted.')
        return redirect('subject_list')
    return render(request, 'students/subject_confirm_delete.html', {'subject': subject})


# ══════════════════════════════════════════════════════════
# Subject-wise Exam Result Entry
# ══════════════════════════════════════════════════════════
@login_required
def exam_subject_results(request, pk):
    from .models import ExamSubjectResult, Subject
    exam = get_object_or_404(Exam, pk=pk)
    subjects = Subject.objects.filter(student_class=exam.student_class).order_by('name')
    students_qs = Student.objects.filter(current_class=exam.student_class, status='active')
    if exam.section:
        students_qs = students_qs.filter(current_section=exam.section)
    students_qs = students_qs.order_by('roll_number', 'user__first_name')

    if request.method == 'POST':
        for student in students_qs:
            for subject in subjects:
                key = f's_{student.pk}_sub_{subject.pk}'
                val = request.POST.get(key, '').strip()
                marks = float(val) if val else None
                ExamSubjectResult.objects.update_or_create(
                    exam=exam, student=student, subject=subject,
                    defaults={
                        'marks_obtained': marks,
                        'full_marks': int(request.POST.get(f'full_{subject.pk}', 100)),
                        'pass_marks': int(request.POST.get(f'pass_{subject.pk}', 33)),
                        'remarks': request.POST.get(f'rem_{student.pk}_{subject.pk}', ''),
                    }
                )
        messages.success(request, 'Subject-wise results saved.')
        return redirect('class_academic_report', pk=pk)

    # Pre-load existing results
    existing = ExamSubjectResult.objects.filter(exam=exam).select_related('student','subject')
    result_map = {}
    for r in existing:
        result_map[(r.student_id, r.subject_id)] = r

    return render(request, 'students/exam_subject_results.html', {
        'exam': exam,
        'subjects': subjects,
        'students': students_qs,
        'result_map': result_map,
    })


# ══════════════════════════════════════════════════════════
# Class Academic Report (All students x All subjects)
# ══════════════════════════════════════════════════════════
@login_required
def class_academic_report(request, pk):
    from .models import ExamSubjectResult, Subject
    exam = get_object_or_404(Exam, pk=pk)
    subjects = Subject.objects.filter(student_class=exam.student_class).order_by('name')
    students_qs = Student.objects.filter(current_class=exam.student_class, status='active')
    if exam.section:
        students_qs = students_qs.filter(current_section=exam.section)
    students_qs = students_qs.order_by('roll_number', 'user__first_name')

    existing = ExamSubjectResult.objects.filter(exam=exam).select_related('student','subject')
    result_map = {}
    for r in existing:
        result_map[(r.student_id, r.subject_id)] = r

    # Build report rows
    rows = []
    for student in students_qs:
        sub_results = []
        total = 0
        full_total = 0
        all_passed = True
        for subject in subjects:
            r = result_map.get((student.pk, subject.pk))
            sub_results.append(r)
            if r and r.marks_obtained is not None:
                total += float(r.marks_obtained)
                full_total += r.full_marks
                if not r.passed:
                    all_passed = False
            else:
                all_passed = False
        pct = round((total / full_total) * 100, 1) if full_total else None
        rows.append({
            'student': student,
            'sub_results': sub_results,
            'total': total,
            'full_total': full_total,
            'percentage': pct,
            'passed': all_passed,
        })

    # Sort by total descending
    rows.sort(key=lambda x: x['total'], reverse=True)
    for i, row in enumerate(rows):
        row['rank'] = i + 1

    return render(request, 'students/class_academic_report.html', {
        'exam': exam,
        'subjects': subjects,
        'rows': rows,
    })


# ══════════════════════════════════════════════════════════
# Module 2: Enhanced Academics (Class Teacher & Homework)
# ══════════════════════════════════════════════════════════

@login_required
def class_teacher_dashboard(request):
    if request.user.role != 'Teacher':
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    assignments = ClassTeacher.objects.filter(teacher=request.user)
    return render(request, 'students/class_teacher_dashboard.html', {'assignments': assignments})

@login_required
def homework_list(request):
    if request.user.role in ['Admin', 'Principal', 'Teacher']:
        homeworks = Homework.objects.all().order_by('-created_at')
        if request.user.role == 'Teacher':
            homeworks = homeworks.filter(teacher=request.user)
    elif request.user.role == 'Student':
        student = getattr(request.user, 'student_profile', None)
        if student:
            homeworks = Homework.objects.filter(student_class=student.current_class).order_by('-created_at')
            if student.section:
                homeworks = homeworks.filter(models.Q(section=student.section) | models.Q(section__isnull=True))
        else:
            homeworks = Homework.objects.none()
    else:
        homeworks = Homework.objects.none()

    return render(request, 'students/homework_list.html', {'homeworks': homeworks})

@login_required
def homework_create(request):
    if request.user.role != 'Teacher':
        messages.error(request, 'Only teachers can create homework.')
        return redirect('homework_list')
    
    if request.method == 'POST':
        student_class_id = request.POST.get('student_class')
        section_id = request.POST.get('section') or None
        subject_id = request.POST.get('subject')
        
        Homework.objects.create(
            student_class_id=student_class_id,
            section_id=section_id,
            subject_id=subject_id,
            teacher=request.user,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            due_date=request.POST.get('due_date'),
            attachment=request.FILES.get('attachment')
        )
        messages.success(request, 'Homework assigned.')
        return redirect('homework_list')

    classes = StudentClass.objects.all()
    subjects = Subject.objects.all()
    return render(request, 'students/homework_form.html', {'classes': classes, 'subjects': subjects})

@login_required
def homework_detail(request, pk):
    homework = get_object_or_404(Homework, pk=pk)
    submissions = homework.submissions.all().select_related('student')
    
    student_submission = None
    if request.user.role == 'Student':
        student = getattr(request.user, 'student_profile', None)
        if student:
            student_submission = submissions.filter(student=student).first()
            
            if request.method == 'POST' and not student_submission:
                HomeworkSubmission.objects.create(
                    homework=homework,
                    student=student,
                    student_remarks=request.POST.get('remarks'),
                    attachment=request.FILES.get('attachment'),
                    status='Submitted'
                )
                messages.success(request, 'Homework submitted successfully.')
                return redirect('homework_detail', pk=pk)

    return render(request, 'students/homework_detail.html', {
        'homework': homework,
        'submissions': submissions,
        'student_submission': student_submission
    })

@login_required
def homework_evaluate(request, pk, sub_pk):
    if request.user.role not in ['Admin', 'Principal', 'Teacher']:
        return redirect('homework_list')
        
    submission = get_object_or_404(HomeworkSubmission, pk=sub_pk, homework_id=pk)
    
    if request.method == 'POST':
        submission.marks_obtained = request.POST.get('marks_obtained')
        submission.teacher_remarks = request.POST.get('teacher_remarks')
        submission.status = 'Evaluated'
        submission.save()
        messages.success(request, 'Submission evaluated.')
        return redirect('homework_detail', pk=pk)
        
    return render(request, 'students/homework_evaluate.html', {'submission': submission})


# ══════════════════════════════════════════════════════════
# Academic Transcript & Merit List
# ══════════════════════════════════════════════════════════

@login_required
def academic_transcript(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    # Ensure privacy
    if request.user.role == 'Student' and getattr(request.user, 'student_profile', None) != student:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
        
    exams = Exam.objects.filter(student_class=student.current_class).order_by('start_date')
    results = ExamSubjectResult.objects.filter(student=student).select_related('exam', 'subject')
    
    # Organize by exam
    data = {}
    total_obtained = 0
    total_max = 0
    for res in results:
        if res.exam not in data:
            data[res.exam] = []
        data[res.exam].append(res)
        if res.marks_obtained:
            total_obtained += res.marks_obtained
            total_max += res.full_marks
            
    final_percentage = round((float(total_obtained) / total_max) * 100, 2) if total_max > 0 else 0
    
    if final_percentage >= 80: final_grade = 'A+'
    elif final_percentage >= 70: final_grade = 'A'
    elif final_percentage >= 60: final_grade = 'B'
    elif final_percentage >= 50: final_grade = 'C'
    elif final_percentage >= 33: final_grade = 'D'
    elif final_percentage > 0: final_grade = 'F'
    else: final_grade = 'N/A'
    
    context = {
        'student': student,
        'data': data,
        'final_percentage': final_percentage,
        'final_grade': final_grade,
        'total_obtained': total_obtained,
        'total_max': total_max,
        'config': SchoolSettings.objects.first()
    }
    return render(request, 'students/academic_transcript.html', context)


@login_required
def class_merit_list(request, class_id):
    student_class = get_object_or_404(StudentClass, pk=class_id)
    
    # Get all students in this class
    students = Student.objects.filter(current_class=student_class, status='Active')
    
    # Calculate total marks for each student across all exams
    rankings = []
    for s in students:
        total = ExamSubjectResult.objects.filter(student=s).aggregate(Sum('marks_obtained'))['marks_obtained__sum'] or 0
        max_m = ExamSubjectResult.objects.filter(student=s, marks_obtained__isnull=False).aggregate(Sum('full_marks'))['full_marks__sum'] or 0
        pct = round((float(total) / max_m) * 100, 2) if max_m > 0 else 0
        rankings.append({
            'student': s,
            'total_marks': total,
            'max_marks': max_m,
            'percentage': pct
        })
        
    # Sort by total marks descending
    rankings.sort(key=lambda x: x['total_marks'], reverse=True)
    
    # Assign Ranks
    for i, r in enumerate(rankings):
        r['rank'] = i + 1

    return render(request, 'students/class_merit_list.html', {
        'student_class': student_class,
        'rankings': rankings,
        'config': SchoolSettings.objects.first()
    })


# ══════════════════════════════════════════════════════════
# Fee Receipt Print
# ══════════════════════════════════════════════════════════

@login_required
def fee_receipt_print(request, payment_id):
    payment = get_object_or_404(FeePayment, pk=payment_id)
    student = payment.student
    config = SchoolSettings.objects.first()
    
    # Calculate Outstanding Balance
    total_fee = student.fee_payments.aggregate(Sum('fee_type__amount'))['fee_type__amount__sum'] or 0
    total_paid = student.fee_payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    outstanding_balance = total_fee - total_paid

    return render(request, 'students/fee_receipt_print.html', {
        'payment': payment,
        'student': student,
        'config': config,
        'outstanding_balance': outstanding_balance
    })


# ══════════════════════════════════════════════════════════
# Attendance Analytics Dashboard
# ══════════════════════════════════════════════════════════

@login_required
def attendance_analytics(request):
    if request.user.role not in ['Admin', 'Principal', 'Teacher']:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
        
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    
    # 1. Overall Stats (Last 30 Days)
    records_last_30 = AttendanceRecord.objects.filter(session__date__gte=thirty_days_ago)
    total_records = records_last_30.count()
    present_count = records_last_30.filter(status='Present').count()
    absent_count = records_last_30.filter(status='Absent').count()
    late_count = records_last_30.filter(status='Late').count()
    
    overall_percentage = round((present_count + late_count) / total_records * 100, 1) if total_records > 0 else 0
    
    # 2. Daily Attendance Trend for Chart (Last 7 Days)
    seven_days_ago = timezone.now().date() - timedelta(days=6)
    sessions = AttendanceSession.objects.filter(date__gte=seven_days_ago).order_by('date')
    
    chart_labels = []
    chart_data_present = []
    chart_data_absent = []
    
    # Aggregate by date
    daily_data = {}
    for session in sessions:
        date_str = session.date.strftime('%b %d')
        if date_str not in daily_data:
            daily_data[date_str] = {'Present': 0, 'Absent': 0, 'Late': 0}
        
        counts = session.records.values('status').annotate(count=Count('status'))
        for c in counts:
            daily_data[date_str][c['status']] += c['count']
            
    for date_str, counts in daily_data.items():
        chart_labels.append(date_str)
        chart_data_present.append(counts['Present'] + counts['Late'])
        chart_data_absent.append(counts['Absent'])
        
    # 3. Students Warning List (Attendance < 75%)
    all_students = Student.objects.filter(status='Active')
    warning_students = []
    
    for student in all_students:
        s_total = AttendanceRecord.objects.filter(student=student).count()
        if s_total > 5: # Only consider if they have at least 5 records
            s_present = AttendanceRecord.objects.filter(student=student, status__in=['Present', 'Late']).count()
            s_pct = (s_present / s_total) * 100
            if s_pct < 75:
                warning_students.append({
                    'student': student,
                    'percentage': round(s_pct, 1),
                    'total_classes': s_total,
                    'absences': s_total - s_present
                })
                
    warning_students.sort(key=lambda x: x['percentage'])
    
    return render(request, 'students/attendance_analytics.html', {
        'overall_percentage': overall_percentage,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'chart_labels': chart_labels,
        'chart_data_present': chart_data_present,
        'chart_data_absent': chart_data_absent,
        'warning_students': warning_students[:10], # Top 10 worst attendance
    })


@login_required
def mark_notifications_read(request):
    # Quick view to mark user's notifications as read
    InAppNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
