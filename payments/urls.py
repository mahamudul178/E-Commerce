# payments/urls.py
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/<uuid:order_id>/', views.process_payment_view, name='process_payment'),
    path('success/<uuid:order_id>/', views.payment_success_view, name='payment_success'),
    path('cancel/<uuid:order_id>/', views.payment_cancel_view, name='payment_cancel'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    
    
    # Stripe webhook
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    
    # Simple payment for testing (when Stripe not configured)
    path('simple/<uuid:order_id>/', views.simple_payment_view, name='simple_payment'),
]