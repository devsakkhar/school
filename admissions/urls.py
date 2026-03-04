from django.urls import path
from . import views

urlpatterns = [
    # Public URLs
    path('apply/', views.apply_admission, name='apply_admission'),
    path('success/', views.admission_success, name='admission_success'),
    
    # Admin URLs
    path('applications/', views.admission_list, name='admission_list'),
    path('applications/<int:pk>/', views.admission_detail, name='admission_detail'),
]
