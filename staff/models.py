from django.db import models
from django.conf import settings
from decimal import Decimal

User = settings.AUTH_USER_MODEL

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    qualification = models.CharField(max_length=200, blank=True, null=True)
    join_date = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Base Salary Structure
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    other_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    provident_fund_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def total_allowances(self):
        return self.medical_allowance + self.transport_allowance + self.other_allowances
        
    def total_fixed_deductions(self):
        return self.provident_fund_deduction + self.tax_deduction

    def __str__(self):
        return f"{self.user.get_full_name()} (Teacher)"

class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('Sick', 'Sick Leave'),
        ('Casual', 'Casual Leave'),
        ('Maternity', 'Maternity Leave'),
        ('Other', 'Other')
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ]
    
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    is_paid_leave = models.BooleanField(default=True, help_text="Uncheck if this is Leave Without Pay (LWP)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_on = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_leaves')
    review_remarks = models.TextField(blank=True, null=True)

    def duration_days(self):
        return (self.end_date - self.start_date).days + 1

    def __str__(self):
        return f"{self.applicant} - {self.leave_type} ({self.status})"

class Payroll(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid')
    ]
    
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payrolls')
    month = models.IntegerField()
    year = models.IntegerField()
    
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # Fixed deductions (PF, Tax, etc)
    fixed_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # Variable deductions (Leave Without Pay)
    leave_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    generated_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payroll: {self.staff} - {self.month}/{self.year}"
    
    def total_deductions(self):
        return self.fixed_deductions + self.leave_deductions
        
    def save(self, *args, **kwargs):
        self.net_salary = self.basic_salary + self.allowances - self.total_deductions()
        super().save(*args, **kwargs)
