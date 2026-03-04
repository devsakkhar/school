from django.db import models
from django.conf import settings

# ══════════════════════════════════════════════════════════
# Asset Management
# ══════════════════════════════════════════════════════════

class AssetCategory(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Asset(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('In Use', 'In Use'),
        ('Maintenance', 'Maintenance'),
        ('Discarded', 'Discarded'),
    ]
    name = models.CharField(max_length=200)
    category = models.ForeignKey(AssetCategory, on_delete=models.CASCADE, related_name='assets')
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.status})"

class AssetAssignment(models.Model):
    STATUS_CHOICES = [
        ('Assigned', 'Assigned'),
        ('Returned', 'Returned'),
    ]
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='assignments')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='asset_assignments')
    assignment_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Assigned')
    remarks = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.asset.name} -> {self.assigned_to.get_full_name()}"

# ══════════════════════════════════════════════════════════
# Expense Management
# ══════════════════════════════════════════════════════════

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

def expense_receipt_upload_path(instance, filename):
    return f"expenses/{instance.date.year}/{instance.date.month}/{filename}"

class Expense(models.Model):
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField()
    receipt = models.FileField(upload_to=expense_receipt_upload_path, null=True, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='recorded_expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.category.name} - ৳{self.amount} on {self.date}"

# ══════════════════════════════════════════════════════════
# Online Payments
# ══════════════════════════════════════════════════════════

class OnlinePaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    ]
    
    # Link to FeeType and Student instead of FeePayment directly
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, null=True, related_name='online_transactions')
    fee_type = models.ForeignKey('students.FeeType', on_delete=models.CASCADE, null=True, related_name='online_transactions')
    
    transaction_id = models.CharField(max_length=150, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='Online Gateway')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.student} - {self.status}"
