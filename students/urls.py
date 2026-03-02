from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('add/', views.student_create, name='student_create'),
    path('<int:pk>/edit/', views.student_update, name='student_update'),
    path('<int:pk>/', views.student_detail, name='student_detail'),
    path('<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('bulk-upload/', views.student_bulk_upload, name='student_bulk_upload'),
    path('bulk-upload/template/', views.student_bulk_upload_template, name='student_bulk_upload_template'),
    path('export-csv/', views.student_export_csv, name='student_export_csv'),
    path('id-cards/', views.generate_id_cards, name='generate_id_cards'),
    path('promote/', views.class_promotion, name='class_promotion'),
    path('settings/', views.school_settings_view, name='school_settings'),
    path('get-sections/', views.get_sections, name='get_sections'),
    
    # Class Management
    path('classes/', views.class_list, name='class_list'),
    path('classes/create/', views.class_create, name='class_create'),
    path('classes/<int:pk>/edit/', views.class_update, name='class_update'),
    path('classes/<int:pk>/delete/', views.class_delete, name='class_delete'),
    
    # Section Management
    path('sections/', views.section_list, name='section_list'),
    path('sections/create/', views.section_create, name='section_create'),
    path('sections/<int:pk>/edit/', views.section_update, name='section_update'),
    path('sections/<int:pk>/delete/', views.section_delete, name='section_delete'),
    
    # Per-Student sub-pages
    path('<int:pk>/remarks/', views.student_remarks, name='student_remarks'),
    path('<int:pk>/remarks/<int:remark_pk>/delete/', views.student_remark_delete, name='student_remark_delete'),
    path('<int:pk>/documents/', views.student_documents, name='student_documents'),
    path('<int:pk>/documents/<int:doc_pk>/delete/', views.student_document_delete, name='student_document_delete'),
    path('<int:pk>/contacts/', views.student_contacts, name='student_contacts'),
    path('<int:pk>/contacts/<int:log_pk>/delete/', views.student_contact_delete, name='student_contact_delete'),
    path('<int:pk>/fee/', views.student_fee, name='student_fee'),
    path('<int:pk>/results/', views.student_report_card, name='student_report_card'),
    
    # Analytics
    path('analytics/', views.student_analytics, name='student_analytics'),
    path('analytics/data/', views.student_analytics_data, name='student_analytics_data'),
    
    # Attendance
    path('attendance/', views.attendance_home, name='attendance_home'),
    path('attendance/take/', views.attendance_take, name='attendance_take'),
    path('attendance/report/', views.attendance_report, name='attendance_report'),
    path('attendance/analytics/', views.attendance_analytics, name='attendance_analytics'),
    
    # Fee Management
    path('fees/', views.fee_list, name='fee_list'),
    path('fees/create/', views.fee_type_create, name='fee_type_create'),
    path('fees/<int:pk>/edit/', views.fee_type_update, name='fee_type_update'),
    path('fees/<int:pk>/delete/', views.fee_type_delete, name='fee_type_delete'),
    path('fees/payments/', views.fee_payments, name='fee_payments'),
    path('fees/record/', views.record_payment, name='record_payment'),
    path('fees/receipt/<int:payment_id>/', views.fee_receipt_print, name='fee_receipt_print'),
    
    # Academic Results
    path('exams/', views.exam_list, name='exam_list'),
    path('exams/create/', views.exam_create, name='exam_create'),
    path('exams/<int:pk>/results/', views.exam_results, name='exam_results'),
    path('exams/<int:pk>/subject-results/', views.exam_subject_results, name='exam_subject_results'),
    path('exams/<int:pk>/delete/', views.exam_delete, name='exam_delete'),

    # Subject Management
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/edit/', views.subject_edit, name='subject_edit'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),

    # Academic Class Report (all students, all subjects, one exam)
    path('exams/<int:pk>/class-report/', views.class_academic_report, name='class_academic_report'),

    # Bulk Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/send/', views.send_notification, name='send_notification'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),

    # Class Teacher & Homework
    path('class-teacher/dashboard/', views.class_teacher_dashboard, name='class_teacher_dashboard'),
    path('homework/', views.homework_list, name='homework_list'),
    path('homework/create/', views.homework_create, name='homework_create'),
    path('homework/<int:pk>/', views.homework_detail, name='homework_detail'),
    path('homework/<int:pk>/evaluate/<int:sub_pk>/', views.homework_evaluate, name='homework_evaluate'),

    # Academic Transcript & Merit List
    path('<int:student_id>/transcript/', views.academic_transcript, name='academic_transcript'),
    path('classes/<int:class_id>/merit-list/', views.class_merit_list, name='class_merit_list'),
]
