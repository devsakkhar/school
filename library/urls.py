from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('', views.library_dashboard, name='library_dashboard'),
    
    # Books CRUD
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.book_create, name='book_create'),
    path('books/<int:pk>/edit/', views.book_update, name='book_update'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),
    
    # Issue / Return
    path('issues/', views.issue_list, name='issue_list'),
    path('issues/new/', views.issue_create, name='issue_create'),
    path('issues/<int:pk>/return/', views.issue_return, name='issue_return'),
    
    # API endpoints for quick add
    path('api/add-author/', api_views.api_add_author, name='api_add_author'),
    path('api/add-category/', api_views.api_add_category, name='api_add_category'),
    
    # Student/User Facing
    path('my-books/', views.my_books, name='my_books'),
]
