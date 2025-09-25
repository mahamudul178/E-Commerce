# Create orders/templatetags/order_extras.py

from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def order_status_badge(status):
    """Return Bootstrap badge HTML for order status"""
    color_map = {
        'pending': 'warning',
        'processing': 'primary',
        'shipped': 'info', 
        'delivered': 'success',
        'cancelled': 'danger',
        'refunded': 'secondary'
    }
    
    icon_map = {
        'pending': 'clock',
        'processing': 'cogs',
        'shipped': 'shipping-fast',
        'delivered': 'check-circle', 
        'cancelled': 'times-circle',
        'refunded': 'undo'
    }
    
    color = color_map.get(status, 'secondary')
    icon = icon_map.get(status, 'question-circle')
    
    return f'<span class="badge bg-{color}"><i class="fas fa-{icon}"></i> {status.title()}</span>'

@register.filter
def can_cancel_order(order):
    """Check if order can be cancelled"""
    return order.status in ['pending', 'processing']

@register.filter
def order_progress_percentage(status):
    """Get progress percentage for order status"""
    progress_map = {
        'pending': 25,
        'processing': 50,
        'shipped': 75,
        'delivered': 100,
        'cancelled': 0,
    }
    return progress_map.get(status, 0)