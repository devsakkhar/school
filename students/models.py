from django.db import models
from django.conf import settings
from django.utils import timezone

class StudentClass(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class StudentSection(models.Model):
    name = models.CharField(max_length=50)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='sections')
    
    class Meta:
        unique_together = ('name', 'student_class')
        
    def __str__(self):
        return f"{self.student_class.name} - {self.name}"

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Alumni', 'Alumni'),
        ('Transferred', 'Transferred'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    # Academic Info
    admission_number = models.CharField(max_length=50, unique=True)
    admission_date = models.DateField()
    current_class = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, null=True, blank=True)
    section = models.ForeignKey(StudentSection, on_delete=models.SET_NULL, null=True, blank=True)
    roll_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Personal Info
    date_of_birth = models.DateField(blank=True, null=True)
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    religion = models.CharField(max_length=50, blank=True, null=True)
    
    # Contact Info
    present_address = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Parent/Guardian Info
    father_name = models.CharField(max_length=100, blank=True, null=True)
    father_phone = models.CharField(max_length=20, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    mother_phone = models.CharField(max_length=20, blank=True, null=True)
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_phone = models.CharField(max_length=20, blank=True, null=True)
    guardian_relation = models.CharField(max_length=50, blank=True, null=True)
    
    # Other
    previous_school = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.admission_number}"

class SchoolSettings(models.Model):
    # Identity
    name = models.CharField(max_length=200, default='School Name')
    tagline = models.CharField(max_length=255, blank=True, null=True, help_text='Short motto or tagline for the school.')
    logo = models.ImageField(upload_to='school_assets/', blank=True, null=True)
    signature = models.ImageField(upload_to='school_assets/', blank=True, null=True)
    
    # Contact
    phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Location
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    
    # Academic
    current_academic_year = models.CharField(max_length=20, blank=True, null=True, help_text='e.g. 2025-2026')
    established_year = models.CharField(max_length=4, blank=True, null=True)
    affiliation = models.CharField(max_length=200, blank=True, null=True, help_text='Board / Affiliation body name')
    
    # Leadership
    principal_name = models.CharField(max_length=150, blank=True, null=True)
    vice_principal_name = models.CharField(max_length=150, blank=True, null=True)
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = 'School Setting'
        verbose_name_plural = 'School Settings'

class PromotionLog(models.Model):
    promoted_at = models.DateTimeField(auto_now_add=True)
    promoted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    from_class = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, null=True, blank=True, related_name='promotions_from')
    to_class = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, null=True, blank=True, related_name='promotions_to')
    to_section = models.ForeignKey(StudentSection, on_delete=models.SET_NULL, null=True, blank=True)
    student_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.promoted_at.strftime('%d %b %Y')} \u2014 {self.student_count} students \u2192 {self.to_class}"

    class Meta:
        ordering = ['-promoted_at']

# ─────────────────────────────────────────
# Student Remarks / Notes
# ─────────────────────────────────────────
class StudentRemark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='remarks')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Remark on {self.student} by {self.author}"

    class Meta:
        ordering = ['-created_at']

# ─────────────────────────────────────────
# Student Documents
# ─────────────────────────────────────────
class StudentDocument(models.Model):
    CATEGORY_CHOICES = [
        ('birth_cert', 'Birth Certificate'),
        ('prev_result', 'Previous Result'),
        ('photo', 'Photo'),
        ('other', 'Other'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    file = models.FileField(upload_to='student_documents/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.student})"

    class Meta:
        ordering = ['-uploaded_at']

# ─────────────────────────────────────────
# Parent Contact Log
# ─────────────────────────────────────────
class ParentContactLog(models.Model):
    METHOD_CHOICES = [
        ('call', 'Phone Call'),
        ('sms', 'SMS'),
        ('in_person', 'In Person'),
        ('email', 'Email'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='contact_logs')
    contacted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    contact_date = models.DateField()
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='call')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} contacted on {self.contact_date}"

    class Meta:
        ordering = ['-contact_date']

# ─────────────────────────────────────────
# Attendance
# ─────────────────────────────────────────
class AttendanceSession(models.Model):
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    section = models.ForeignKey(StudentSection, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student_class', 'section', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student_class} - {self.date}"

class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('leave', 'On Leave'),
    ]
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')

    class Meta:
        unique_together = ('session', 'student')

    def __str__(self):
        return f"{self.student} - {self.status} on {self.session.date}"

# ─────────────────────────────────────────
# Fee Management
# ─────────────────────────────────────────
class FeeType(models.Model):
    name = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    academic_year = models.CharField(max_length=20, blank=True)
    due_date = models.DateField(null=True, blank=True)
    applies_to_class = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, null=True, blank=True, help_text='Leave blank for all classes')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.academic_year})"

    class Meta:
        ordering = ['name']

class FeePayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_payments')
    fee_type = models.ForeignKey(FeeType, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} paid {self.fee_type} on {self.payment_date}"

    class Meta:
        ordering = ['-payment_date']

# ─────────────────────────────────────────
# Academic Results
# ─────────────────────────────────────────
class Exam(models.Model):
    name = models.CharField(max_length=200)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    section = models.ForeignKey(StudentSection, on_delete=models.SET_NULL, null=True, blank=True)
    exam_date = models.DateField()
    total_marks = models.PositiveIntegerField(default=100)
    pass_marks = models.PositiveIntegerField(default=33)
    academic_year = models.CharField(max_length=20, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.student_class}"

    class Meta:
        ordering = ['-exam_date']

class StudentResult(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    grade = models.CharField(max_length=5, blank=True)
    remarks = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ('exam', 'student')

    def __str__(self):
        return f"{self.student} in {self.exam}"
    
    def save(self, *args, **kwargs):
        if self.marks_obtained is not None:
            pct = (self.marks_obtained / self.exam.total_marks) * 100
            if pct >= 80: self.grade = 'A+'
            elif pct >= 70: self.grade = 'A'
            elif pct >= 60: self.grade = 'B'
            elif pct >= 50: self.grade = 'C'
            elif pct >= 33: self.grade = 'D'
            else: self.grade = 'F'
        super().save(*args, **kwargs)


# ══════════════════════════════════════════════════════════
# Module 2: Enhanced Academics
# ══════════════════════════════════════════════════════════



def homework_upload_path(instance, filename):
    return f"homework/{instance.student_class.id}/{instance.subject.id}/{filename}"

class Homework(models.Model):
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    section = models.ForeignKey(StudentSection, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    attachment = models.FileField(upload_to=homework_upload_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.student_class} - {self.subject})"

def submission_upload_path(instance, filename):
    return f"homework_submissions/{instance.homework.id}/{instance.student.id}/{filename}"

class HomeworkSubmission(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Submitted', 'Submitted'),
        ('Evaluated', 'Evaluated')
    ]
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='homework_submissions')
    submission_date = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to=submission_upload_path, null=True, blank=True)
    student_remarks = models.TextField(blank=True, null=True)
    teacher_remarks = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Submitted')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)

    class Meta:
        unique_together = ('homework', 'student')

    def __str__(self):
        return f"{self.student} - {self.homework.title} ({self.status})"
# ─────────────────────────────────────────
# Bulk Notification
# ─────────────────────────────────────────
class BulkNotification(models.Model):
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    recipient_class = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, null=True, blank=True, help_text='Leave blank for all classes')
    recipient_status = models.CharField(max_length=20, blank=True, help_text='Leave blank for all statuses')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    recipient_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.subject} ({self.sent_at.strftime('%d %b %Y')})"

    class Meta:
        ordering = ['-sent_at']




# ══════ Subject Management ═══════════════════════════════
class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)
    student_class = models.ForeignKey('StudentClass', on_delete=models.CASCADE, related_name='subjects')
    teacher_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f'{self.name} ({self.student_class})'

    class Meta:
        unique_together = ('name', 'student_class')
        ordering = ['student_class', 'name']


# ══════ Class Teacher Assignment ══════════════════════════
class ClassTeacher(models.Model):
    student_class = models.ForeignKey('StudentClass', on_delete=models.CASCADE, related_name='class_teachers')
    section = models.ForeignKey('StudentSection', on_delete=models.SET_NULL, null=True, blank=True)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='class_assignments')
    academic_year = models.CharField(max_length=20, blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student_class} -- {self.teacher.get_full_name()}'

    class Meta:
        unique_together = ('student_class', 'section', 'academic_year')
        ordering = ['student_class']


# ══════ Subject-wise Exam Result ══════════════════════════
class ExamSubjectResult(models.Model):
    """Stores per-subject marks for a student in a specific exam."""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='subject_results')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='subject_results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exam_results')
    full_marks = models.PositiveIntegerField(default=100)
    pass_marks = models.PositiveIntegerField(default=33)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    grade = models.CharField(max_length=5, blank=True)
    remarks = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ('exam', 'student', 'subject')
        ordering = ['student', 'subject']

    def __str__(self):
        return f"{self.student} | {self.subject.name} | {self.exam.name}"

    @property
    def percentage(self):
        if self.marks_obtained is not None and self.full_marks:
            return round((float(self.marks_obtained) / self.full_marks) * 100, 1)
        return None

    @property
    def passed(self):
        return self.marks_obtained is not None and self.marks_obtained >= self.pass_marks

    def save(self, *args, **kwargs):
        if self.marks_obtained is not None:
            pct = (float(self.marks_obtained) / self.full_marks) * 100
            if pct >= 80:   self.grade = 'A+'
            elif pct >= 70: self.grade = 'A'
            elif pct >= 60: self.grade = 'B'
            elif pct >= 50: self.grade = 'C'
            elif pct >= 33: self.grade = 'D'
            else:           self.grade = 'F'
        super().save(*args, **kwargs)

# ══════════════════════════════════════════════════════════
# In-App Notifications
# ══════════════════════════════════════════════════════════

class InAppNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.title}"

# ══════════════════════════════════════════════════════════
# Disciplinary Tracking
# ══════════════════════════════════════════════════════════
class DisciplinaryRecord(models.Model):
    SEVERITY_CHOICES = [
        ('Low', 'Low - Warning'),
        ('Medium', 'Medium - Detention/Call'),
        ('High', 'High - Suspension/Expulsion'),
        ('Positive', 'Positive - Award/Commendation')
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='disciplinary_records')
    incident_date = models.DateField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    action_taken = models.TextField(blank=True, null=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='Low')
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.severity}] {self.student.user.get_full_name()} - {self.title}"

    class Meta:
        ordering = ['-incident_date', '-created_at']

# ══════════════════════════════════════════════════════════
# Alumni Management
# ══════════════════════════════════════════════════════════
class AlumniProfile(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='alumni_profile')
    graduation_year = models.IntegerField()
    current_profession = models.CharField(max_length=200, blank=True, null=True)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    higher_education_info = models.TextField(blank=True, null=True, help_text="Details about university or college attended after graduation.")
    achievements = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Alumni: {self.student.user.get_full_name()} ({self.graduation_year})"
