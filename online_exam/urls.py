from django.urls import path
from . import views

urlpatterns = [
    # Question Bank
    path('questions/', views.question_bank, name='question_bank'),
    path('questions/create/', views.question_create, name='question_create'),
    path('questions/<int:pk>/edit/', views.question_edit, name='question_edit'),
    path('questions/<int:pk>/delete/', views.question_delete, name='question_delete'),

    # Exams
    path('exams/', views.exam_list, name='online_exam_list'),
    path('exams/create/', views.exam_create, name='online_exam_create'),
    path('exams/<int:pk>/', views.exam_detail, name='online_exam_detail'),
    path('exams/<int:pk>/edit/', views.exam_edit, name='online_exam_edit'),
    path('exams/<int:pk>/delete/', views.exam_delete, name='online_exam_delete'),
    path('exams/<int:pk>/add-questions/', views.exam_add_questions, name='online_exam_add_questions'),

    # Student — Take Exam
    path('exams/<int:pk>/take/', views.exam_take, name='exam_take'),
    path('exams/<int:pk>/submit/', views.exam_submit, name='exam_submit'),
    path('exams/<int:pk>/result/', views.exam_result, name='exam_result'),

    # Leaderboard / attempts
    path('exams/<int:pk>/attempts/', views.exam_attempts, name='exam_attempts'),
]
