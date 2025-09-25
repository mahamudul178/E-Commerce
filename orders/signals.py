# Create orders/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Order

@receiver(pre_save, sender=Order)
def track_status_change(sender, instance, **kwargs):
    """Track order status changes"""
    if instance.pk:  # Only for existing orders
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

@receiver(post_save, sender=Order)
def handle_status_change(sender, instance, created, **kwargs):
    """Handle order status changes"""
    if not created:  # Only for updates
        old_status = getattr(instance, '_old_status', None)
        
        if old_status and old_status != instance.status:
            # Status changed - send notification
            send_order_status_notification(instance, old_status)
            
            # Log status change (optional)
            print(f"Order {instance.order_number} status changed: {old_status} → {instance.status}")

# Don't forget to add this to your orders/apps.py:
"""
from django.apps import AppConfig

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
    
    def ready(self):
        import orders.signals
"""