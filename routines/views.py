from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import ClassRoutine, ExamRoutineEntry, CalendarEvent
from students.models import StudentClass, StudentSection


# ── AJAX helper ─────────────────────────────────────────────────────────────
def get_sections_ajax(request):
    class_id = request.GET.get('class_id')
    sections = list(StudentSection.objects.filter(student_class_id=class_id).values('id', 'name'))
    return JsonResponse({'sections': sections})


# ── Class Routine ────────────────────────────────────────────────────────────
@login_required
def class_routine_home(request):
    classes = StudentClass.objects.all()
    class_id = request.GET.get('class_id')
    section_id = request.GET.get('section_id')
    sections = StudentSection.objects.filter(student_class_id=class_id) if class_id else []
    entries = []
    days = ['saturday', 'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    day_entries = {}

    if class_id:
        qs = ClassRoutine.objects.filter(student_class_id=class_id)
        if section_id:
            qs = qs.filter(section_id=section_id)
        qs = qs.order_by('day', 'period_number')
        for entry in qs:
            day_entries.setdefault(entry.day, []).append(entry)

    return render(request, 'routines/class_routine_home.html', {
        'classes': classes, 'sections': sections, 'class_id': class_id,
        'section_id': section_id, 'days': days, 'day_entries': day_entries,
    })

@login_required
def class_routine_create(request):
    classes = StudentClass.objects.all()
    if request.method == 'POST':
        class_obj = get_object_or_404(StudentClass, pk=request.POST.get('student_class'))
        section = StudentSection.objects.filter(pk=request.POST.get('section')).first()
        ClassRoutine.objects.create(
            student_class=class_obj, section=section,
            day=request.POST.get('day'),
            period_number=request.POST.get('period_number', 1),
            subject_name=request.POST.get('subject_name'),
            teacher_name=request.POST.get('teacher_name', ''),
            start_time=request.POST.get('start_time'),
            end_time=request.POST.get('end_time'),
            room=request.POST.get('room', ''),
        )
        messages.success(request, 'Routine entry added.')
        return redirect(f"{request.path.replace('create/', '')}?class_id={class_obj.pk}")
    return render(request, 'routines/class_routine_form.html', {
        'classes': classes, 'action': 'Add',
        'day_choices': ClassRoutine.DAY_CHOICES,
    })

@login_required
def class_routine_edit(request, pk):
    entry = get_object_or_404(ClassRoutine, pk=pk)
    classes = StudentClass.objects.all()
    sections = StudentSection.objects.filter(student_class=entry.student_class)
    if request.method == 'POST':
        entry.student_class = get_object_or_404(StudentClass, pk=request.POST.get('student_class'))
        entry.section = StudentSection.objects.filter(pk=request.POST.get('section')).first()
        entry.day = request.POST.get('day')
        entry.period_number = request.POST.get('period_number', 1)
        entry.subject_name = request.POST.get('subject_name')
        entry.teacher_name = request.POST.get('teacher_name', '')
        entry.start_time = request.POST.get('start_time')
        entry.end_time = request.POST.get('end_time')
        entry.room = request.POST.get('room', '')
        entry.save()
        messages.success(request, 'Routine updated.')
        return redirect(f'/routines/class-routine/?class_id={entry.student_class.pk}')
    return render(request, 'routines/class_routine_form.html', {
        'entry': entry, 'classes': classes, 'sections': sections, 'action': 'Edit',
        'day_choices': ClassRoutine.DAY_CHOICES,
    })

@login_required
def class_routine_delete(request, pk):
    entry = get_object_or_404(ClassRoutine, pk=pk)
    class_id = entry.student_class.pk
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Routine entry deleted.')
        return redirect(f'/routines/class-routine/?class_id={class_id}')
    return render(request, 'routines/confirm_delete.html', {'title': 'Routine Entry', 'object': entry, 'cancel_url': f'/routines/class-routine/?class_id={class_id}'})


# ── Exam Routine ─────────────────────────────────────────────────────────────
@login_required
def exam_routine_home(request):
    classes = StudentClass.objects.all()
    class_id = request.GET.get('class_id')
    exam_name = request.GET.get('exam_name', '')
    entries = ExamRoutineEntry.objects.all()
    if class_id:
        entries = entries.filter(student_class_id=class_id)
    if exam_name:
        entries = entries.filter(exam_name__icontains=exam_name)
    distinct_exams = ExamRoutineEntry.objects.values_list('exam_name', flat=True).distinct()
    return render(request, 'routines/exam_routine_home.html', {
        'entries': entries, 'classes': classes, 'class_id': class_id,
        'exam_name': exam_name, 'distinct_exams': distinct_exams,
    })

@login_required
def exam_routine_create(request):
    classes = StudentClass.objects.all()
    if request.method == 'POST':
        ExamRoutineEntry.objects.create(
            exam_name=request.POST.get('exam_name'),
            student_class=get_object_or_404(StudentClass, pk=request.POST.get('student_class')),
            section=StudentSection.objects.filter(pk=request.POST.get('section')).first(),
            subject=request.POST.get('subject'),
            exam_date=request.POST.get('exam_date'),
            start_time=request.POST.get('start_time'),
            end_time=request.POST.get('end_time'),
            room=request.POST.get('room', ''),
            academic_year=request.POST.get('academic_year', ''),
        )
        messages.success(request, 'Exam routine entry added.')
        return redirect('exam_routine_home')
    return render(request, 'routines/exam_routine_form.html', {'classes': classes, 'action': 'Add'})

@login_required
def exam_routine_edit(request, pk):
    entry = get_object_or_404(ExamRoutineEntry, pk=pk)
    classes = StudentClass.objects.all()
    if request.method == 'POST':
        entry.exam_name = request.POST.get('exam_name')
        entry.student_class = get_object_or_404(StudentClass, pk=request.POST.get('student_class'))
        entry.section = StudentSection.objects.filter(pk=request.POST.get('section')).first()
        entry.subject = request.POST.get('subject')
        entry.exam_date = request.POST.get('exam_date')
        entry.start_time = request.POST.get('start_time')
        entry.end_time = request.POST.get('end_time')
        entry.room = request.POST.get('room', '')
        entry.academic_year = request.POST.get('academic_year', '')
        entry.save()
        messages.success(request, 'Exam routine updated.')
        return redirect('exam_routine_home')
    return render(request, 'routines/exam_routine_form.html', {'entry': entry, 'classes': classes, 'action': 'Edit'})

@login_required
def exam_routine_delete(request, pk):
    entry = get_object_or_404(ExamRoutineEntry, pk=pk)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Exam routine entry deleted.')
        return redirect('exam_routine_home')
    return render(request, 'routines/confirm_delete.html', {'title': 'Exam Routine Entry', 'object': entry, 'cancel_url': '/routines/exam-routine/'})


# ── Year Calendar ────────────────────────────────────────────────────────────
@login_required
def year_calendar(request):
    events = CalendarEvent.objects.all()
    event_type = request.GET.get('event_type', '')
    if event_type:
        events = events.filter(event_type=event_type)
    event_types = CalendarEvent.EVENT_TYPES
    # Build JSON for calendar rendering
    import json
    events_json = json.dumps([
        {
            'id': e.pk,
            'title': e.title,
            'start': str(e.start_date),
            'end': str(e.end_date) if e.end_date else str(e.start_date),
            'type': e.event_type,
            'color': {
                'holiday': '#dc3545', 'exam': '#007bff', 'activity': '#28a745',
                'meeting': '#fd7e14', 'result': '#6f42c1', 'other': '#6c757d',
            }.get(e.event_type, '#6c757d'),
        }
        for e in events
    ])
    return render(request, 'routines/year_calendar.html', {
        'events': events, 'events_json': events_json, 'event_types': event_types, 'event_type': event_type,
    })

@login_required
def calendar_event_create(request):
    if request.method == 'POST':
        classes = StudentClass.objects.filter(pk=request.POST.get('student_class')).first()
        CalendarEvent.objects.create(
            title=request.POST.get('title'),
            event_type=request.POST.get('event_type', 'other'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date') or None,
            description=request.POST.get('description', ''),
            applies_to_all=request.POST.get('applies_to_all') == 'on',
            student_class=classes,
        )
        messages.success(request, 'Event added to calendar.')
        return redirect('year_calendar')
    classes = StudentClass.objects.all()
    return render(request, 'routines/calendar_event_form.html', {
        'classes': classes, 'action': 'Add',
        'event_types': CalendarEvent.EVENT_TYPES,
    })

@login_required
def calendar_event_edit(request, pk):
    event = get_object_or_404(CalendarEvent, pk=pk)
    classes = StudentClass.objects.all()
    if request.method == 'POST':
        event.title = request.POST.get('title')
        event.event_type = request.POST.get('event_type', 'other')
        event.start_date = request.POST.get('start_date')
        event.end_date = request.POST.get('end_date') or None
        event.description = request.POST.get('description', '')
        event.applies_to_all = request.POST.get('applies_to_all') == 'on'
        event.student_class = StudentClass.objects.filter(pk=request.POST.get('student_class')).first()
        event.save()
        messages.success(request, 'Event updated.')
        return redirect('year_calendar')
    return render(request, 'routines/calendar_event_form.html', {
        'event': event, 'classes': classes, 'action': 'Edit',
        'event_types': CalendarEvent.EVENT_TYPES,
    })

@login_required
def calendar_event_delete(request, pk):
    event = get_object_or_404(CalendarEvent, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted.')
        return redirect('year_calendar')
    return render(request, 'routines/confirm_delete.html', {'title': 'Calendar Event', 'object': event, 'cancel_url': '/routines/calendar/'})
