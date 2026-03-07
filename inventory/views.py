from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Sum, F
from .models import ItemCategory, Supplier, Item, StockTransaction
from .forms import ItemCategoryForm, SupplierForm, ItemForm, StockTransactionForm

@login_required
def dashboard(request):
    total_items = Item.objects.count()
    low_stock_items = Item.objects.filter(current_stock__lte=F('min_stock_level'))
    recent_transactions = StockTransaction.objects.select_related('item', 'supplier').all()[:10]
    
    context = {
        'total_items': total_items,
        'low_stock_count': low_stock_items.count(),
        'low_stock_items': low_stock_items[:5],
        'recent_transactions': recent_transactions
    }
    return render(request, 'inventory/dashboard.html', context)

# ══════════════════════════════════════════════════════════
# Categories
# ══════════════════════════════════════════════════════════
@login_required
def category_list(request):
    categories = ItemCategory.objects.all()
    return render(request, 'inventory/category_list.html', {'categories': categories})

@login_required
def category_form(request, pk=None):
    category = get_object_or_404(ItemCategory, pk=pk) if pk else None
    form = ItemCategoryForm(request.POST or None, instance=category)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category saved successfully.')
        return redirect('inventory_category_list')
    return render(request, 'inventory/form.html', {'form': form, 'title': 'Category Form', 'cancel_url': 'inventory_category_list'})

# ══════════════════════════════════════════════════════════
# Suppliers
# ══════════════════════════════════════════════════════════
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})

@login_required
def supplier_form(request, pk=None):
    supplier = get_object_or_404(Supplier, pk=pk) if pk else None
    form = SupplierForm(request.POST or None, instance=supplier)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Supplier saved successfully.')
        return redirect('inventory_supplier_list')
    return render(request, 'inventory/form.html', {'form': form, 'title': 'Supplier Form', 'cancel_url': 'inventory_supplier_list'})

# ══════════════════════════════════════════════════════════
# Items
# ══════════════════════════════════════════════════════════
@login_required
def item_list(request):
    items = Item.objects.select_related('category').all()
    return render(request, 'inventory/item_list.html', {'items': items})

@login_required
def item_form(request, pk=None):
    item = get_object_or_404(Item, pk=pk) if pk else None
    form = ItemForm(request.POST or None, instance=item)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Item saved successfully.')
        return redirect('inventory_item_list')
    return render(request, 'inventory/form.html', {'form': form, 'title': 'Item Form', 'cancel_url': 'inventory_item_list'})

# ══════════════════════════════════════════════════════════
# Transactions (Issue / Add Stock)
# ══════════════════════════════════════════════════════════
@login_required
def transaction_list(request):
    transactions = StockTransaction.objects.select_related('item', 'supplier', 'recorded_by').all()
    return render(request, 'inventory/transaction_list.html', {'transactions': transactions})

@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = StockTransactionForm(request.POST)
        if form.is_valid():
            trans = form.save(commit=False)
            trans.recorded_by = request.user
            
            # Validation: Block OUT transactions if stock insufficient
            item = trans.item
            if trans.transaction_type in ['OUT', 'ADJ']:
                if item.current_stock < trans.quantity:
                    messages.error(request, f'Insufficient stock! Current stock: {item.current_stock} {item.unit}')
                    return render(request, 'inventory/transaction_form.html', {'form': form})
            
            trans.save()
            messages.success(request, 'Transaction recorded successfully.')
            return redirect('inventory_transaction_list')
    else:
        form = StockTransactionForm()
        
    return render(request, 'inventory/transaction_form.html', {'form': form})
