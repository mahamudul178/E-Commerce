# Create orders/templatetags/order_status.py
from django import template
from orders.models import Order

register = template.Library()

@register.simple_tag
def user_order_count(user, status=None):
    """Get order count for user, optionally filtered by status"""
    if not user.is_authenticated:
        return 0
    
    orders = Order.objects.filter(user=user)
    if status:
        orders = orders.filter(status=status)
    
    return orders.count()

@register.simple_tag
def user_has_pending_orders(user):
    """Check if user has any pending orders"""
    if not user.is_authenticated:
        return False
    
    return Order.objects.filter(user=user, status='pending').exists()

@register.simple_tag
def user_latest_order(user):
    """Get user's latest order"""
    if not user.is_authenticated:
        return None
    
    return Order.objects.filter(user=user).order_by('-created_at').first()