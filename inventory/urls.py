from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='inventory_dashboard'),
    
    path('categories/', views.category_list, name='inventory_category_list'),
    path('categories/add/', views.category_form, name='inventory_category_add'),
    path('categories/<int:pk>/edit/', views.category_form, name='inventory_category_edit'),
    
    path('suppliers/', views.supplier_list, name='inventory_supplier_list'),
    path('suppliers/add/', views.supplier_form, name='inventory_supplier_add'),
    path('suppliers/<int:pk>/edit/', views.supplier_form, name='inventory_supplier_edit'),
    
    path('items/', views.item_list, name='inventory_item_list'),
    path('items/add/', views.item_form, name='inventory_item_add'),
    path('items/<int:pk>/edit/', views.item_form, name='inventory_item_edit'),
    
    path('transactions/', views.transaction_list, name='inventory_transaction_list'),
    path('transactions/new/', views.transaction_create, name='inventory_transaction_add'),
]
