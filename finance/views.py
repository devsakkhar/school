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
def asset_create(request):
    if request.user.role not in ['Admin', 'Principal']:
        messages.error(request, 'Access denied.')
        return redirect('index')
        
    from .forms import AssetForm
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asset created successfully.')
            return redirect('asset_list')
    else:
        form = AssetForm()
    return render(request, 'finance/asset_form.html', {'form': form, 'title': 'Add New Asset'})

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

# ══════════════════════════════════════════════════════════
# Online Payment Gateway (Mock Integration)
# ══════════════════════════════════════════════════════════
import uuid
from django.utils import timezone
from .models import OnlinePaymentTransaction
from students.models import FeeType, FeePayment, Student

@login_required
def initiate_payment(request, fee_type_id):
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Only students can initiate payments.')
        return redirect('index')
        
    fee_type = get_object_or_404(FeeType, pk=fee_type_id)
    
    # Check if a pending transaction already exists, if so reuse it, else create new
    transaction = OnlinePaymentTransaction.objects.filter(student=student, fee_type=fee_type, status='Pending').first()
    if not transaction:
        transaction = OnlinePaymentTransaction.objects.create(
            student=student,
            fee_type=fee_type,
            transaction_id=f"TXN-{uuid.uuid4().hex[:10].upper()}",
            amount=fee_type.amount,
        )
        
    context = {
        'transaction': transaction,
        'fee_type': fee_type,
        'student': student,
    }
    return render(request, 'finance/mock_payment_gateway.html', context)

@login_required
def payment_callback(request, transaction_id):
    transaction = get_object_or_404(OnlinePaymentTransaction, transaction_id=transaction_id)
    status = request.GET.get('status', 'Failed')
    
    if status == 'Success' and transaction.status != 'Success':
        transaction.status = 'Success'
        transaction.save()
        
        # Create the FeePayment record
        FeePayment.objects.create(
            student=transaction.student,
            fee_type=transaction.fee_type,
            amount_paid=transaction.amount,
            payment_date=timezone.now().date(),
            received_by=None, # Online payment
            notes=f"Paid via Online Gateway. TXN: {transaction.transaction_id}"
        )
        
        messages.success(request, f"Payment successful for {transaction.fee_type.name}.")
    elif status != 'Success':
        transaction.status = 'Failed'
        transaction.save()
        messages.error(request, 'Payment failed or cancelled.')
        
    return redirect('student_dashboard')
