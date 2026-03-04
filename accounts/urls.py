from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='accounts/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
    
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Role Management
    path('roles/', views.role_list, name='role_list'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/<int:pk>/update/', views.role_update, name='role_update'),
    path('roles/<int:pk>/delete/', views.role_delete, name='role_delete'),
    
    # User Management
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/update/', views.user_update, name='user_update'),
    # Notice Board
    path('notices/', views.notice_list, name='notice_list'),
    path('notices/create/', views.notice_create, name='notice_create'),
    path('notices/<int:pk>/update/', views.notice_update, name='notice_update'),
    path('notices/<int:pk>/delete/', views.notice_delete, name='notice_delete'),
]
