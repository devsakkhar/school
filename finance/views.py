from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import AssetCategory, Asset, AssetAssignment, ExpenseCategory, Expense

# ══════════════════════════════════════════════════════════
# Asset Management Views
# ══════════════════════════════════════════════════════════

@login_required
def asset_list(request):
    assets = Asset.objects.all().select_related('category')
    return render(request, 'finance/asset_list.html', {'assets': assets})

@login_required
def asset_assignment_list(request):
    assignments = AssetAssignment.objects.all().select_related('asset', 'assigned_to')
    return render(request, 'finance/asset_assignment.html', {'assignments': assignments})

# ══════════════════════════════════════════════════════════
# Expense Management Views
# ══════════════════════════════════════════════════════════

@login_required
def expense_list(request):
    expenses = Expense.objects.all().select_related('category', 'recorded_by').order_by('-date', '-created_at')
    
    # Calculate total expenses for simple summary
    total_amount = sum(exp.amount for exp in expenses)
    
    context = {
        'expenses': expenses,
        'total_amount': total_amount,
    }
    return render(request, 'finance/expense_list.html', context)
