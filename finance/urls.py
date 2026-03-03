from django.urls import path
from . import views

urlpatterns = [
    # Asset Management
    path('assets/', views.asset_list, name='asset_list'),
    path('asset-assignments/', views.asset_assignment_list, name='asset_assignment_list'),
    
    # Expense Management
    path('expenses/', views.expense_list, name='expense_list'),
]
