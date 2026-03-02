from django.db import models
from django.conf import settings
from students.models import StudentClass, StudentSection, Student

User = settings.AUTH_USER_MODEL


class QuestionBank(models.Model):
    DIFFICULTY_CHOICES = [('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')]
    OPTION_CHOICES = [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]

    subject = models.CharField(max_length=100)
    student_class = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    marks = models.PositiveIntegerField(default=1)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} — {self.question_text[:60]}"

    class Meta:
        ordering = ['-created_at']


class OnlineExam(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('active', 'Active'), ('closed', 'Closed')]

    name = models.CharField(max_length=200)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='online_exams')
    section = models.ForeignKey(StudentSection, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=30, help_text='Duration in minutes')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_marks = models.PositiveIntegerField(default=0)
    pass_marks = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.student_class})"

    @property
    def question_count(self):
        return self.exam_questions.count()

    class Meta:
        ordering = ['-created_at']


class ExamQuestion(models.Model):
    exam = models.ForeignKey(OnlineExam, on_delete=models.CASCADE, related_name='exam_questions')
    question = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('exam', 'question')


class ExamAttempt(models.Model):
    STATUS_CHOICES = [('in_progress', 'In Progress'), ('submitted', 'Submitted'), ('timed_out', 'Timed Out')]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_attempts')
    exam = models.ForeignKey(OnlineExam, on_delete=models.CASCADE, related_name='attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='in_progress')

    class Meta:
        unique_together = ('student', 'exam')

    def __str__(self):
        return f"{self.student} — {self.exam.name}"

    @property
    def percentage(self):
        if self.score and self.exam.total_marks:
            return round(self.score / self.exam.total_marks * 100, 1)
        return 0

    @property
    def passed(self):
        return self.score is not None and self.score >= self.exam.pass_marks


class AttemptAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')], null=True, blank=True)
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('attempt', 'question')
