from django.db import models
from django.conf import settings
from students.models import FeePayment

class OnlinePaymentTransaction(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    ]
    
    fee_payment = models.ForeignKey(FeePayment, on_delete=models.CASCADE, related_name='online_transactions')
    transaction_id = models.CharField(max_length=150, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='bKash/Cards')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.status}"
