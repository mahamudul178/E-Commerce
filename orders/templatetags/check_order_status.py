from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from orders.models import Order
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Check order status and send notifications'
    
    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, help='Check orders for specific user')
        parser.add_argument('--status', type=str, help='Check orders with specific status')
        parser.add_argument('--days', type=int, default=7, help='Check orders from last N days')
    
    def handle(self, *args, **options):
        user_id = options.get('user_id')
        status = options.get('status')
        days = options.get('days')
        
        # Filter orders
        orders = Order.objects.all()
        
        if user_id:
            orders = orders.filter(user_id=user_id)
        
        if status:
            orders = orders.filter(status=status)
        
        # Filter by date range
        date_threshold = timezone.now() - timedelta(days=days)
        orders = orders.filter(created_at__gte=date_threshold)
        
        # Display results
        self.stdout.write(f"Found {orders.count()} orders")
        
        for order in orders:
            self.stdout.write(
                f"Order {order.order_number}: "
                f"Status={order.status}, "
                f"User={order.user.username}, "
                f"Total=${order.total}, "
                f"Created={order.created_at.date()}"
            )
            
        # Check for orders that need attention
        stuck_orders = Order.objects.filter(
            status='pending',
            created_at__lt=timezone.now() - timedelta(days=3)
        )
        
        if stuck_orders.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️ {stuck_orders.count()} orders have been pending for more than 3 days"
                )
            )