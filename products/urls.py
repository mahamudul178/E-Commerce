# products/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list_view, name='product_list'),
    path('category/<slug:slug>/', views.category_view, name='category'),
    path('<slug:slug>/', views.product_detail_view, name='product_detail'),
]