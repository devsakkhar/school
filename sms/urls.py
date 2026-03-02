from django.urls import path
from . import views

urlpatterns = [
    path('', views.send_sms, name='send_sms'),
    path('history/', views.sms_history, name='sms_history'),
]
