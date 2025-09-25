# accounts/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView, PasswordResetDoneView, PasswordResetCompleteView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    # Profile Management URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/picture/', views.update_profile_picture_view, name='update_profile_picture'),
    
    # Email Verification URLs
    path('verify-email-sent/', views.verify_email_sent_view, name='verify_email_sent'),
    path('verify/<str:uidb64>/<str:token>/', views.verify_email_view, name='verify_email'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),
    
    # Password Management URLs
    path('password/change/', views.change_password_view, name='change_password'),
    path('password/reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password/reset/done/', PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/complete/', PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
    
    # Address Management URLs
    path('address/add/', views.add_address_view, name='add_address'),
    path('address/edit/<int:address_id>/', views.edit_address_view, name='edit_address'),
    path('address/delete/<int:address_id>/', views.delete_address_view, name='delete_address'),
    
    # Account Settings URLs
    path('settings/', views.account_settings_view, name='account_settings'),
    path('delete/', views.delete_account_view, name='delete_account'),  # New URL pattern
    
    # Google login redirect
    path('google-login/', views.google_login_redirect, name='google_login'),


# Google OAuth completion
    path('complete-google-profile/', views.complete_google_profile, name='complete_google_profile'),
    path('social-signup-success/', views.social_signup_success, name='social_signup_success'),


]