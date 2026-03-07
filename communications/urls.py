from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.send_bulk_message, name='send_bulk_message'),
    path('logs/', views.message_logs, name='message_logs'),
]
