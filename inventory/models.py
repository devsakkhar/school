from django.db import models
from django.conf import settings

class ItemCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Item Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE, related_name='items')
    description = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=50, default='pcs', help_text="e.g. pcs, kg, box, packet")
    min_stock_level = models.PositiveIntegerField(default=5, help_text="Alert if stock falls below this level")
    current_stock = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"

class StockTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'Stock In (Purchase/Add)'),
        ('OUT', 'Stock Out (Issue/Consume)'),
        ('ADJ', 'Stock Adjustment (Lost/Damaged)'),
    ]
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField()
    transaction_date = models.DateField(auto_now_add=True)
    
    # For IN transactions
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='supplied_stocks')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # For OUT transactions
    issued_to = models.CharField(max_length=200, blank=True, null=True, help_text="Student, Teacher, or Department Name")
    
    remarks = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-transaction_date', '-id']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.item.name} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        # We handle stock adjustments strictly on creation.
        # If modifying past transactions, the system needs complex rebuilds. For simplicity, we only track on creation.
        if is_new:
            if self.transaction_type == 'IN':
                self.item.current_stock += self.quantity
            elif self.transaction_type in ['OUT', 'ADJ']:
                self.item.current_stock -= self.quantity
            self.item.save()
            
        super().save(*args, **kwargs)
