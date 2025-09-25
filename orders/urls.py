# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [

    
    path('checkout/', views.checkout_view, name='checkout'),
    path('', views.order_list_view, name='order_list'),
    path('<uuid:order_id>/', views.order_detail_view, name='order_detail'),
    
    # Add these new URLs:
    path('cancel/<uuid:order_id>/', views.cancel_order_view, name='cancel_order'),
    path('reorder/<uuid:order_id>/', views.reorder_view, name='reorder'),


    path('dashboard/', views.user_order_status_view, name='order_dashboard'),
    path('api/stats/', views.user_order_stats_api, name='order_stats_api'),
    path('api/status/<uuid:order_id>/', views.check_order_status_api, name='order_status_api'),
    path('track/<str:order_number>/', views.order_tracking_api, name='order_tracking_api'),



]