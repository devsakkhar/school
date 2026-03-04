from django.urls import path
from . import views

urlpatterns = [
    # Asset Management
    path('assets/', views.asset_list, name='asset_list'),
    path('assets/create/', views.asset_create, name='asset_create'),
    path('asset-assignments/', views.asset_assignment_list, name='asset_assignment_list'),
    
    # Expense Management
    path('expenses/', views.expense_list, name='expense_list'),
    
    # Online Payments
    path('pay/<int:fee_type_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment-callback/<str:transaction_id>/', views.payment_callback, name='payment_callback'),
]
