from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
from cart.utils import get_or_create_cart
from accounts.models import Address
from .models import Order, OrderItem
from .forms import CheckoutForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from cart.models import CartItem


@login_required
def checkout_view(request):
    cart = get_or_create_cart(request)
    
    if not cart or not cart.items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')
    
    # Check stock availability
    for item in cart.items.all():
        if item.quantity > item.product.stock:
            messages.error(request, f'Only {item.product.stock} {item.product.name} available in stock.')
            return redirect('cart:cart_detail')
    
    # Calculate order totals
    subtotal = cart.get_total_price()
    shipping_cost = Decimal('10.00')
    tax_rate = Decimal('0.08')  # 8% tax
    tax_amount = subtotal * tax_rate
    total = subtotal + shipping_cost + tax_amount
    
    user_addresses = Address.objects.filter(user=request.user)
    default_address = user_addresses.filter(is_default=True).first()
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            # Create order
            order = Order.objects.create(
                user=request.user,
                billing_name=form.cleaned_data['billing_name'],
                billing_email=form.cleaned_data['billing_email'],
                billing_phone=form.cleaned_data['billing_phone'],
                billing_address_1=form.cleaned_data['billing_address_1'],
                billing_address_2=form.cleaned_data['billing_address_2'],
                billing_city=form.cleaned_data['billing_city'],
                billing_state=form.cleaned_data['billing_state'],
                billing_postal_code=form.cleaned_data['billing_postal_code'],
                billing_country=form.cleaned_data['billing_country'],
                shipping_name=form.cleaned_data['shipping_name'],
                shipping_phone=form.cleaned_data['shipping_phone'],
                shipping_address_1=form.cleaned_data['shipping_address_1'],
                shipping_address_2=form.cleaned_data['shipping_address_2'],
                shipping_city=form.cleaned_data['shipping_city'],
                shipping_state=form.cleaned_data['shipping_state'],
                shipping_postal_code=form.cleaned_data['shipping_postal_code'],
                shipping_country=form.cleaned_data['shipping_country'],
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                tax_amount=tax_amount,
                total=total,
            )
            
            # Create order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity
                )
                
                # Update product stock
                cart_item.product.stock -= cart_item.quantity
                cart_item.product.save()
            
            # Clear cart
            cart.items.all().delete()
            
            # Redirect to payment
            return redirect('payments:process_payment', order_id=order.id)
    else:
        initial_data = {}
        if default_address:
            initial_data = {
                'billing_name': default_address.full_name,
                'billing_email': default_address.email,
                'billing_phone': default_address.phone,
                'billing_address_1': default_address.address_line_1,
                'billing_address_2': default_address.address_line_2,
                'billing_city': default_address.city,
                'billing_state': default_address.state,
                'billing_postal_code': default_address.postal_code,
                'billing_country': default_address.country,
                'shipping_name': default_address.full_name,
                'shipping_phone': default_address.phone,
                'shipping_address_1': default_address.address_line_1,
                'shipping_address_2': default_address.address_line_2,
                'shipping_city': default_address.city,
                'shipping_state': default_address.state,
                'shipping_postal_code': default_address.postal_code,
                'shipping_country': default_address.country,
            }
        
        form = CheckoutForm(initial=initial_data, user=request.user)
    
    context = {
        'form': form,
        'cart': cart,
        'user_addresses': user_addresses,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'tax_amount': tax_amount,
        'tax_rate': tax_rate,
        'tax_rate_percent': int(tax_rate * 100),  # For display (8%)
        'total': total,
    }
    return render(request, 'orders/checkout.html', context)



@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'orders/order_detail.html', context)

@login_required
def order_list_view(request):
    orders = Order.objects.filter(user=request.user)
    context = {'orders': orders}
    return render(request, 'orders/order_list.html', context)




@login_required
@require_POST
def reorder_view(request, order_id):
    """Add all items from an existing order back to the cart"""
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        cart = get_or_create_cart(request)
        
        items_added = 0
        items_out_of_stock = []
        
        for order_item in order.items.all():
            # Check if product still exists and is active
            if order_item.product and order_item.product.is_active and order_item.product.stock > 0:
                # Get or create cart item
                from cart.models import CartItem
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=order_item.product,
                    defaults={'quantity': min(order_item.quantity, order_item.product.stock)}
                )
                
                if not created:
                    # Update quantity if item already in cart
                    new_quantity = cart_item.quantity + min(order_item.quantity, order_item.product.stock - cart_item.quantity)
                    cart_item.quantity = new_quantity
                    cart_item.save()
                
                items_added += 1
            else:
                items_out_of_stock.append(order_item.product_name)
        
        if items_added > 0:
            message = f'{items_added} items added to your cart.'
            
            if items_out_of_stock:
                message += f' Note: {len(items_out_of_stock)} items are out of stock and were not added.'

                
            messages.success(request, message)
            # return JsonResponse({
            #     'success': True,
            #     'message': message,
            #     'items_added': items_added,
            #     'items_out_of_stock': items_out_of_stock,
            #     'redirect_url': '/cart/'
            # })
            
        else:
            return JsonResponse({
                'success': False,
                'message': 'No items could be added to cart. All items are out of stock.'
            })
            
        return redirect('cart:cart_detail')
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error adding items to cart. Please try again.'
        })


from django.views.decorators.http import require_POST
@login_required
@require_POST
def cancel_order_view(request, order_id):
    """Cancel an order if it's in pending or processing status"""
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        # Check if order can be cancelled
        if order.status not in ['pending', 'processing']:
            return JsonResponse({
                'success': False,
                'message': f'This order cannot be cancelled as it is already {order.status}.'
            })
        
        # Store old status for logging
        old_status = order.status
        
        # Update order status
        order.status = 'cancelled'
        order.save()
        
        # Restore product stock
        items_restored = 0
        for item in order.items.all():
            if item.product:  # Make sure product still exists
                item.product.stock += item.quantity
                item.product.save()
                items_restored += 1
        
        # If payment was completed, you might want to initiate refund
        if order.payment_status == 'completed':
            order.payment_status = 'refunded'
            order.save()
            # Here you would integrate with your payment processor to issue refund
            # For example, with Stripe:
            # stripe.Refund.create(payment_intent=order.payment_id)
        
        messages.success(request, f'Order {order.order_number} has been cancelled successfully.')
        return redirect('orders:order_detail', order_id=order.id)
        # return JsonResponse({
        #     'success': True,
        #     'message': f'Order {order.order_number} has been cancelled successfully.',
        #     'order_status': order.status,
        #     'items_restored': items_restored
        # })
        
    except Exception as e:
        messages.error(request, 'Error cancelling order. Please try again or contact support.')
        return JsonResponse({
            'success': False,
            'message': 'Error cancelling order. Please try again or contact support.',
            'error': str(e)
        })



#---------------------------- Order Tracking and Status Checking-----------------------


# orders/views.py - Add these methods

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Q
from .models import Order
from django.utils import timezone
from datetime import timedelta

@login_required
def user_order_status_view(request):
    """Check all order statuses for the current user"""
    user = request.user
    
    # Get all orders for user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    # Count orders by status
    status_counts = Order.objects.filter(user=user).aggregate(
        total_orders=Count('id'),
        pending_orders=Count('id', filter=Q(status='pending')),
        processing_orders=Count('id', filter=Q(status='processing')),
        shipped_orders=Count('id', filter=Q(status='shipped')),
        delivered_orders=Count('id', filter=Q(status='delivered')),
        cancelled_orders=Count('id', filter=Q(status='cancelled')),
    )
    
    # Get recent orders by status
    recent_pending = orders.filter(status='pending')[:5]
    recent_processing = orders.filter(status='processing')[:5]
    recent_shipped = orders.filter(status='shipped')[:5]
    recent_delivered = orders.filter(status='delivered')[:5]
    
    context = {
        'orders': orders,
        'status_counts': status_counts,
        'recent_pending': recent_pending,
        'recent_processing': recent_processing,
        'recent_shipped': recent_shipped,
        'recent_delivered': recent_delivered,
    }
    
    return render(request, 'orders/order_status_dashboard.html', context)

def check_order_status_api(request, order_id):
    """API endpoint to check specific order status"""
    try:
        if request.user.is_authenticated:
            order = get_object_or_404(Order, id=order_id, user=request.user)
        else:
            # For guest users, you might use session or order number
            order = get_object_or_404(Order, id=order_id)
        
        # Calculate order progress
        progress_percentage = get_order_progress(order.status)
        
        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'status': order.status,
            'payment_status': order.payment_status,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': order.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'progress_percentage': progress_percentage,
            'status_display': order.get_status_display(),
            'can_cancel': order.status in ['pending', 'processing'],
            'tracking_info': get_tracking_info(order),
        })
    
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Order not found'
        }, status=404)

# ========================================
# 2. UTILITY FUNCTIONS FOR ORDER TRACKING
# ========================================

def get_order_progress(status):
    """Calculate order progress percentage based on status"""
    progress_map = {
        'pending': 10,
        'processing': 30,
        'shipped': 70,
        'delivered': 100,
        'cancelled': 0,
        'refunded': 0,
    }
    return progress_map.get(status, 0)

def get_tracking_info(order):
    """Get tracking information for an order"""
    tracking_info = {
        'order_placed': {
            'completed': True,
            'date': order.created_at.strftime('%Y-%m-%d'),
            'description': 'Order has been placed successfully'
        },
        'processing': {
            'completed': order.status in ['processing', 'shipped', 'delivered'],
            'date': order.updated_at.strftime('%Y-%m-%d') if order.status in ['processing', 'shipped', 'delivered'] else None,
            'description': 'Order is being prepared for shipment'
        },
        'shipped': {
            'completed': order.status in ['shipped', 'delivered'],
            'date': order.updated_at.strftime('%Y-%m-%d') if order.status in ['shipped', 'delivered'] else None,
            'description': 'Order has been shipped'
        },
        'delivered': {
            'completed': order.status == 'delivered',
            'date': order.updated_at.strftime('%Y-%m-%d') if order.status == 'delivered' else None,
            'description': 'Order has been delivered'
        }
    }
    
    return tracking_info

def user_has_orders(user):
    """Check if user has any orders"""
    return Order.objects.filter(user=user).exists()

def get_user_order_summary(user):
    """Get comprehensive order summary for a user"""
    if not user.is_authenticated:
        return None
    
    orders = Order.objects.filter(user=user)
    
    summary = {
        'total_orders': orders.count(),
        'total_spent': sum(order.total for order in orders),
        'pending_orders': orders.filter(status='pending').count(),
        'processing_orders': orders.filter(status='processing').count(),
        'shipped_orders': orders.filter(status='shipped').count(),
        'delivered_orders': orders.filter(status='delivered').count(),
        'cancelled_orders': orders.filter(status='cancelled').count(),
        'recent_order': orders.order_by('-created_at').first(),
        'needs_attention': orders.filter(
            Q(status='pending', created_at__lt=timezone.now() - timedelta(days=3)) |
            Q(status='processing', updated_at__lt=timezone.now() - timedelta(days=7))
        ).count()
    }
    
    return summary




def some_view(request):
    user = request.user
    
    # Check if user has any orders
    if user_has_orders(user):
        print("User has orders")
    
    # Get order summary
    summary = get_user_order_summary(user)
    print(f"User has {summary['pending_orders']} pending orders")
    
    # Check specific order
    order = Order.objects.filter(user=user).first()
    if order:
        if order.is_pending():
            print("Order is pending")
        elif order.is_processing():
            print("Order is being processed")
        elif order.is_shipped():
            print("Order has been shipped")
        elif order.is_delivered():
            print("Order has been delivered")
            
            
            
# Add these to orders/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json

@login_required
@require_http_methods(["GET"])
def user_order_stats_api(request):
    """API endpoint to get user's order statistics"""
    user = request.user
    
    stats = {
        'total_orders': Order.objects.filter(user=user).count(),
        'pending_orders': Order.objects.filter(user=user, status='pending').count(),
        'processing_orders': Order.objects.filter(user=user, status='processing').count(),
        'shipped_orders': Order.objects.filter(user=user, status='shipped').count(),
        'delivered_orders': Order.objects.filter(user=user, status='delivered').count(),
        'cancelled_orders': Order.objects.filter(user=user, status='cancelled').count(),
        'total_spent': float(sum(order.total for order in Order.objects.filter(user=user))),
        'average_order_value': 0,
        'most_recent_order': None,
    }
    
    if stats['total_orders'] > 0:
        stats['average_order_value'] = stats['total_spent'] / stats['total_orders']
        
        recent_order = Order.objects.filter(user=user).order_by('-created_at').first()
        if recent_order:
            stats['most_recent_order'] = {
                'order_number': recent_order.order_number,
                'status': recent_order.status,
                'total': float(recent_order.total),
                'created_at': recent_order.created_at.isoformat(),
            }
    
    return JsonResponse(stats)

@require_http_methods(["GET"])
def order_tracking_api(request, order_number):
    """Public API for order tracking by order number"""
    try:
        order = Order.objects.get(order_number=order_number)
        
        # Basic security check - you might want to add more validation
        email = request.GET.get('email')
        if email and order.billing_email.lower() != email.lower():
            return JsonResponse({'error': 'Invalid credentials'}, status=403)
        
        tracking_info = {
            'order_number': order.order_number,
            'status': order.status,
            'payment_status': order.payment_status,
            'total': float(order.total),
            'created_at': order.created_at.isoformat(),
            'updated_at': order.updated_at.isoformat(),
            'tracking_steps': [
                {
                    'step': 'order_placed',
                    'title': 'Order Placed',
                    'completed': True,
                    'date': order.created_at.isoformat(),
                    'description': 'Your order has been received and confirmed.'
                },
                {
                    'step': 'processing',
                    'title': 'Processing',
                    'completed': order.status in ['processing', 'shipped', 'delivered'],
                    'date': order.updated_at.isoformat() if order.status in ['processing', 'shipped', 'delivered'] else None,
                    'description': 'Your order is being prepared for shipment.'
                },
                {
                    'step': 'shipped',
                    'title': 'Shipped',
                    'completed': order.status in ['shipped', 'delivered'],
                    'date': order.updated_at.isoformat() if order.status in ['shipped', 'delivered'] else None,
                    'description': 'Your order has been shipped and is on its way.'
                },
                {
                    'step': 'delivered',
                    'title': 'Delivered',
                    'completed': order.status == 'delivered',
                    'date': order.updated_at.isoformat() if order.status == 'delivered' else None,
                    'description': 'Your order has been delivered successfully.'
                }
            ]
        }
        
        return JsonResponse(tracking_info)
        
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)


from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_order_status_notification(order, old_status=None):
    """Send email notification when order status changes"""
    
    # Define email templates for each status
    templates = {
        'processing': {
            'subject': f'Order {order.order_number} is being processed',
            'template': 'emails/order_processing.html'
        },
        'shipped': {
            'subject': f'Order {order.order_number} has been shipped',
            'template': 'emails/order_shipped.html'
        },
        'delivered': {
            'subject': f'Order {order.order_number} has been delivered',
            'template': 'emails/order_delivered.html'
        }
    }
    
    if order.status in templates:
        template_info = templates[order.status]
        
        context = {
            'order': order,
            'user': order.user,
            'old_status': old_status,
        }
        
        html_message = render_to_string(template_info['template'], context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=template_info['subject'],
            message=plain_message,
            from_email='noreply@shopease.com',
            recipient_list=[order.billing_email],
            html_message=html_message,
            fail_silently=True,
        )







