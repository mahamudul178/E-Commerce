from .models import Order
from django.utils import timezone
from datetime import timedelta

def get_user_order_summary(user):
    """Return a summary of the user's orders."""
    orders = Order.objects.filter(user=user)
    return {
        'total_orders': orders.count(),
        'recent_order': orders.order_by('-created_at').first(),
    }

def user_has_orders(user):
    """Return True if the user has any orders, False otherwise."""
    return Order.objects.filter(user=user).exists()

def user_orders_context(request):
    """Add user order information to all templates"""
    if request.user.is_authenticated:
        order_summary = get_user_order_summary(request.user)
        return {
            'user_order_summary': order_summary,
            'user_has_orders': user_has_orders(request.user),
        }
    return {}