from django.db import models

# Create your models here.
# orders/models.py
from django.db import models
from django.contrib.auth.models import User
from products.models import Product
import uuid
from django.utils import timezone
from datetime import timedelta

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Billing Information
    billing_name = models.CharField(max_length=100)
    billing_email = models.EmailField()
    billing_phone = models.CharField(max_length=20)
    billing_address_1 = models.CharField(max_length=100)
    billing_address_2 = models.CharField(max_length=100, blank=True)
    billing_city = models.CharField(max_length=50)
    billing_state = models.CharField(max_length=50)
    billing_postal_code = models.CharField(max_length=20)
    billing_country = models.CharField(max_length=50)
    
    # Shipping Information
    shipping_name = models.CharField(max_length=100)
    shipping_phone = models.CharField(max_length=20)
    shipping_address_1 = models.CharField(max_length=100)
    shipping_address_2 = models.CharField(max_length=100, blank=True)
    shipping_city = models.CharField(max_length=50)
    shipping_state = models.CharField(max_length=50)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=50)
    
    # Order totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment info
    payment_method = models.CharField(max_length=50, blank=True)
    payment_id = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{str(self.id).split('-')[0].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)  # Store product name at time of order
    product_price = models.DecimalField(max_digits=10, decimal_places=2)  # Store price at time of order
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        self.product_name = self.product.name
        self.product_price = self.product.price
        self.total_price = self.product_price * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
    
    
    
    
    
# ---------------------------- Order Tracking and Status Checking-----------------------
    def get_status_color(self):
        """Get Bootstrap color class for status"""
        color_map = {
            'pending': 'warning',
            'processing': 'primary', 
            'shipped': 'info',
            'delivered': 'success',
            'cancelled': 'danger',
            'refunded': 'secondary'
        }
        return color_map.get(self.status, 'secondary')
    
    def get_status_icon(self):
        """Get FontAwesome icon for status"""
        icon_map = {
            'pending': 'fas fa-clock',
            'processing': 'fas fa-cogs',
            'shipped': 'fas fa-shipping-fast',
            'delivered': 'fas fa-check-circle',
            'cancelled': 'fas fa-times-circle',
            'refunded': 'fas fa-undo'
        }
        return icon_map.get(self.status, 'fas fa-question-circle')
    
    def is_pending(self):
        """Check if order is pending"""
        return self.status == 'pending'
    
    def is_processing(self):
        """Check if order is being processed"""
        return self.status == 'processing'
    
    def is_shipped(self):
        """Check if order has been shipped"""
        return self.status == 'shipped'
    
    def is_delivered(self):
        """Check if order has been delivered"""
        return self.status == 'delivered'
    
    def is_cancelled(self):
        """Check if order is cancelled"""
        return self.status == 'cancelled'
    
    def can_be_cancelled(self):
        """Check if order can still be cancelled"""
        return self.status in ['pending', 'processing']
    
    def can_be_returned(self):
        """Check if order can be returned (within 30 days of delivery)"""
        if self.status != 'delivered':
            return False
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return self.updated_at > thirty_days_ago
    
    def days_since_order(self):
        """Get number of days since order was placed"""
        return (timezone.now() - self.created_at).days
    
    def estimated_delivery_date(self):
        """Calculate estimated delivery date"""
        if self.status == 'delivered':
            return None
        
        # Estimate based on shipping method (you can customize this)
        if self.status == 'shipped':
            return self.updated_at + timedelta(days=3)
        elif self.status == 'processing':
            return timezone.now() + timedelta(days=5)
        else:
            return timezone.now() + timedelta(days=7)
    
    def get_status_display_color(self):
        """Get hex color for status display"""
        color_map = {
            'pending': '#ffc107',
            'processing': '#0d6efd',
            'shipped': '#0dcaf0',
            'delivered': '#198754',
            'cancelled': '#dc3545',
            'refunded': '#6c757d'
        }
        return color_map.get(self.status, '#6c757d')
        
        
        
# Add these methods to your Order model in orders/models.py
