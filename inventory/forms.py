from django import forms
from .models import ItemCategory, Supplier, Item, StockTransaction

class ItemCategoryForm(forms.ModelForm):
    class Meta:
        model = ItemCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'category', 'description', 'unit', 'min_stock_level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. pcs, box, kg'}),
            'min_stock_level': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class StockTransactionForm(forms.ModelForm):
    class Meta:
        model = StockTransaction
        fields = ['item', 'transaction_type', 'quantity', 'supplier', 'unit_price', 'issued_to', 'remarks']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select', 'id': 'transType'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'supplier': forms.Select(attrs={'class': 'form-select supplier-field'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control supplier-field'}),
            'issued_to': forms.TextInput(attrs={'class': 'form-control issue-field'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
