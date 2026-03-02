from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Sum

from .models import QuestionBank, OnlineExam, ExamQuestion, ExamAttempt, AttemptAnswer
from students.models import Student, StudentClass, StudentSection


# ── Question Bank ────────────────────────────────────────────────────────────
@login_required
def question_bank(request):
    qs = QuestionBank.objects.select_related('student_class', 'created_by').all()
    subject = request.GET.get('subject', '')
    class_id = request.GET.get('class_id', '')
    difficulty = request.GET.get('difficulty', '')
    if subject:
        qs = qs.filter(subject__icontains=subject)
    if class_id:
        qs = qs.filter(student_class_id=class_id)
    if difficulty:
        qs = qs.filter(difficulty=difficulty)
    classes = StudentClass.objects.all()
    return render(request, 'online_exam/question_bank.html', {
        'questions': qs, 'classes': classes,
        'subject': subject, 'class_id': class_id, 'difficulty': difficulty,
        'difficulty_choices': QuestionBank.DIFFICULTY_CHOICES,
    })

@login_required
def question_create(request):
    classes = StudentClass.objects.all()
    if request.method == 'POST':
        QuestionBank.objects.create(
            subject=request.POST.get('subject'),
            student_class=StudentClass.objects.filter(pk=request.POST.get('student_class')).first(),
            question_text=request.POST.get('question_text'),
            option_a=request.POST.get('option_a'),
            option_b=request.POST.get('option_b'),
            option_c=request.POST.get('option_c'),
            option_d=request.POST.get('option_d'),
            correct_option=request.POST.get('correct_option'),
            marks=request.POST.get('marks', 1),
            difficulty=request.POST.get('difficulty', 'medium'),
            created_by=request.user,
        )
        messages.success(request, 'Question added to bank.')
        next_action = request.POST.get('next', 'bank')
        return redirect('question_create' if next_action == 'add_another' else 'question_bank')
    return render(request, 'online_exam/question_form.html', {
        'classes': classes, 'action': 'Add',
        'option_choices': QuestionBank.OPTION_CHOICES,
        'difficulty_choices': QuestionBank.DIFFICULTY_CHOICES,
    })

@login_required
def question_edit(request, pk):
    question = get_object_or_404(QuestionBank, pk=pk)
    classes = StudentClass.objects.all()
    if request.method == 'POST':
        question.subject = request.POST.get('subject')
        question.student_class = StudentClass.objects.filter(pk=request.POST.get('student_class')).first()
        question.question_text = request.POST.get('question_text')
        question.option_a = request.POST.get('option_a')
        question.option_b = request.POST.get('option_b')
        question.option_c = request.POST.get('option_c')
        question.option_d = request.POST.get('option_d')
        question.correct_option = request.POST.get('correct_option')
        question.marks = request.POST.get('marks', 1)
        question.difficulty = request.POST.get('difficulty', 'medium')
        question.save()
        messages.success(request, 'Question updated.')
        return redirect('question_bank')
    return render(request, 'online_exam/question_form.html', {
        'question': question, 'classes': classes, 'action': 'Edit',
        'option_choices': QuestionBank.OPTION_CHOICES,
        'difficulty_choices': QuestionBank.DIFFICULTY_CHOICES,
    })

@login_required
def question_delete(request, pk):
    question = get_object_or_404(QuestionBank, pk=pk)
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted.')
        return redirect('question_bank')
    return render(request, 'online_exam/question_confirm_delete.html', {'question': question})


# ── Online Exams ─────────────────────────────────────────────────────────────
@login_required
def exam_list(request):
    exams = OnlineExam.objects.select_related('student_class', 'section', 'created_by').annotate(
        q_count=Count('exam_questions'),
        attempt_count=Count('attempts'),
    )
    classes = StudentClass.objects.all()
    class_id = request.GET.get('class_id')
    if class_id:
        exams = exams.filter(student_class_id=class_id)
    return render(request, 'online_exam/exam_list.html', {'exams': exams, 'classes': classes, 'class_id': class_id})

@login_required
def exam_create(request):
    classes = StudentClass.objects.all()
    if request.method == 'POST':
        class_obj = get_object_or_404(StudentClass, pk=request.POST.get('student_class'))
        section = StudentSection.objects.filter(pk=request.POST.get('section')).first()
        OnlineExam.objects.create(
            name=request.POST.get('name'),
            student_class=class_obj,
            section=section,
            subject=request.POST.get('subject'),
            instructions=request.POST.get('instructions', ''),
            duration_minutes=request.POST.get('duration_minutes', 30),
            start_time=request.POST.get('start_time'),
            end_time=request.POST.get('end_time'),
            total_marks=request.POST.get('total_marks', 0),
            pass_marks=request.POST.get('pass_marks', 0),
            status=request.POST.get('status', 'draft'),
            created_by=request.user,
        )
        messages.success(request, 'Online exam created.')
        return redirect('online_exam_list')
    return render(request, 'online_exam/exam_form.html', {'classes': classes, 'action': 'Create', 'status_choices': OnlineExam.STATUS_CHOICES})

@login_required
def exam_detail(request, pk):
    exam = get_object_or_404(OnlineExam, pk=pk)
    exam_questions = exam.exam_questions.select_related('question').all()
    attempts = exam.attempts.select_related('student__user').order_by('-score')[:20]
    return render(request, 'online_exam/exam_detail.html', {'exam': exam, 'exam_questions': exam_questions, 'attempts': attempts})

@login_required
def exam_edit(request, pk):
    exam = get_object_or_404(OnlineExam, pk=pk)
    classes = StudentClass.objects.all()
    sections = StudentSection.objects.filter(student_class=exam.student_class)
    if request.method == 'POST':
        exam.name = request.POST.get('name')
        exam.student_class = get_object_or_404(StudentClass, pk=request.POST.get('student_class'))
        exam.section = StudentSection.objects.filter(pk=request.POST.get('section')).first()
        exam.subject = request.POST.get('subject')
        exam.instructions = request.POST.get('instructions', '')
        exam.duration_minutes = request.POST.get('duration_minutes', 30)
        exam.start_time = request.POST.get('start_time')
        exam.end_time = request.POST.get('end_time')
        exam.total_marks = request.POST.get('total_marks', 0)
        exam.pass_marks = request.POST.get('pass_marks', 0)
        exam.status = request.POST.get('status', 'draft')
        exam.save()
        messages.success(request, 'Exam updated.')
        return redirect('online_exam_detail', pk=pk)
    return render(request, 'online_exam/exam_form.html', {'exam': exam, 'classes': classes, 'sections': sections, 'action': 'Edit', 'status_choices': OnlineExam.STATUS_CHOICES})

@login_required
def exam_delete(request, pk):
    exam = get_object_or_404(OnlineExam, pk=pk)
    if request.method == 'POST':
        exam.delete()
        messages.success(request, 'Exam deleted.')
        return redirect('online_exam_list')
    return render(request, 'online_exam/exam_confirm_delete.html', {'exam': exam})

@login_required
def exam_add_questions(request, pk):
    exam = get_object_or_404(OnlineExam, pk=pk)
    # Get questions for this exam's class and subject
    available = QuestionBank.objects.filter(
        student_class=exam.student_class
    ).exclude(
        exam_questions__exam=exam
    )
    added = exam.exam_questions.select_related('question').all()

    if request.method == 'POST':
        action = request.POST.get('action')
        q_id = request.POST.get('question_id')
        if action == 'add' and q_id:
            question = get_object_or_404(QuestionBank, pk=q_id)
            eq, created = ExamQuestion.objects.get_or_create(exam=exam, question=question, defaults={'order': exam.exam_questions.count() + 1})
            if created:
                # Recalculate total marks
                exam.total_marks = exam.exam_questions.aggregate(total=Sum('question__marks'))['total'] or 0
                exam.save()
                messages.success(request, 'Question added to exam.')
        elif action == 'remove' and q_id:
            ExamQuestion.objects.filter(exam=exam, question_id=q_id).delete()
            exam.total_marks = exam.exam_questions.aggregate(total=Sum('question__marks'))['total'] or 0
            exam.save()
            messages.success(request, 'Question removed.')
        return redirect('online_exam_add_questions', pk=pk)
    return render(request, 'online_exam/exam_add_questions.html', {'exam': exam, 'available': available, 'added': added})


# ── Student: Take Exam ───────────────────────────────────────────────────────
@login_required
def exam_take(request, pk):
    exam = get_object_or_404(OnlineExam, pk=pk, status='active')
    try:
        student = request.user.student_profile
    except AttributeError:
        messages.error(request, 'Only students can take exams.')
        return redirect('online_exam_list')

    # Check if already submitted
    attempt = ExamAttempt.objects.filter(student=student, exam=exam).first()
    if attempt and attempt.status == 'submitted':
        return redirect('exam_result', pk=pk)

    now = timezone.now()
    if now < exam.start_time:
        messages.warning(request, f'Exam starts at {exam.start_time.strftime("%d %b %Y, %H:%M")}.')
        return redirect('online_exam_list')
    if now > exam.end_time:
        messages.warning(request, 'This exam has ended.')
        return redirect('online_exam_list')

    if not attempt:
        attempt = ExamAttempt.objects.create(student=student, exam=exam)

    questions = exam.exam_questions.select_related('question').all()
    time_left = int((exam.end_time - now).total_seconds())

    if request.method == 'POST':
        return redirect('exam_submit', pk=pk)

    return render(request, 'online_exam/exam_take.html', {
        'exam': exam, 'attempt': attempt, 'questions': questions, 'time_left': time_left,
    })

@login_required
def exam_submit(request, pk):
    exam = get_object_or_404(OnlineExam, pk=pk)
    try:
        student = request.user.student_profile
    except AttributeError:
        return redirect('online_exam_list')

    attempt = get_object_or_404(ExamAttempt, student=student, exam=exam)
    if attempt.status == 'submitted':
        return redirect('exam_result', pk=pk)

    if request.method == 'POST':
        score = 0
        for eq in exam.exam_questions.select_related('question').all():
            q = eq.question
            selected = request.POST.get(f'q_{q.pk}', '').strip()
            correct = (selected == q.correct_option)
            AttemptAnswer.objects.update_or_create(
                attempt=attempt, question=q,
                defaults={'selected_option': selected or None, 'is_correct': correct}
            )
            if correct:
                score += q.marks
        attempt.score = score
        attempt.status = 'submitted'
        attempt.submitted_at = timezone.now()
        attempt.save()
        messages.success(request, f'Exam submitted. Your score: {score}/{exam.total_marks}')
        return redirect('exam_result', pk=pk)
    return redirect('exam_take', pk=pk)

@login_required
def exam_result(request, pk):
    exam = get_object_or_404(OnlineExam, pk=pk)
    try:
        student = request.user.student_profile
        attempt = get_object_or_404(ExamAttempt, student=student, exam=exam)
    except AttributeError:
        attempt = None
    answers = attempt.answers.select_related('question').all() if attempt else []
    return render(request, 'online_exam/exam_result.html', {'exam': exam, 'attempt': attempt, 'answers': answers})

@login_required
def exam_attempts(request, pk):
    exam = get_object_or_404(OnlineExam, pk=pk)
    attempts = exam.attempts.select_related('student__user').order_by('-score')
    return render(request, 'online_exam/exam_attempts.html', {'exam': exam, 'attempts': attempts})
