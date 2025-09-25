from django.shortcuts import render

# Create your views here.
# payments/views.py
import stripe
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from orders.models import Order
import json

# stripe.api_key = settings.STRIPE_SECRET_KEY

# @login_required
# def process_payment_view(request, order_id):
#     order = get_object_or_404(Order, id=order_id, user=request.user, payment_status='pending')
    
#     if request.method == 'POST':
#         try:
#             # Create Stripe Payment Intent
#             intent = stripe.PaymentIntent.create(
#                 amount=int(order.total * 100),  # Stripe uses cents
#                 currency='usd',
#                 metadata={
#                     'order_id': str(order.id),
#                     'order_number': order.order_number,
#                 }
#             )
            
#             context = {
#                 'order': order,
#                 'client_secret': intent.client_secret,
#                 'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
#             }
#             return render(request, 'payments/payment.html', context)
            
#         except stripe.error.StripeError as e:
#             messages.error(request, f'Payment error: {e.user_message}')
#             return redirect('orders:order_detail', order_id=order.id)
    
#     context = {
#         'order': order,
#         'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
#     }
#     return render(request, 'payments/process_payment.html', context)

# @login_required
# def payment_success_view(request, order_id):
#     order = get_object_or_404(Order, id=order_id, user=request.user)
    
#     # Update order status
#     order.payment_status = 'completed'
#     order.status = 'processing'
#     order.save()
    
#     # Send confirmation email (optional)
#     # send_order_confirmation_email(order)
    
#     messages.success(request, f'Payment successful! Your order {order.order_number} has been placed.')
    
#     context = {'order': order}
#     return render(request, 'payments/payment_success.html', context)

# @login_required
# def payment_cancel_view(request, order_id):
#     order = get_object_or_404(Order, id=order_id, user=request.user)
#     messages.warning(request, 'Payment was cancelled. You can try again anytime.')
#     return redirect('orders:order_detail', order_id=order.id)

# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
#     endpoint_secret = settings.STRIPE_WEBHOOK_SECRET if hasattr(settings, 'STRIPE_WEBHOOK_SECRET') else None
    
#     try:
#         if endpoint_secret:
#             event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
#         else:
#             event = json.loads(payload)
#     except ValueError:
#         return HttpResponse(status=400)
#     except stripe.error.SignatureVerificationError:
#         return HttpResponse(status=400)
    
#     # Handle the event
#     if event['type'] == 'payment_intent.succeeded':
#         payment_intent = event['data']['object']
#         order_id = payment_intent['metadata']['order_id']
        
#         try:
#             order = Order.objects.get(id=order_id)
#             order.payment_status = 'completed'
#             order.status = 'processing'
#             order.payment_id = payment_intent['id']
#             order.payment_method = 'stripe'
#             order.save()
#         except Order.DoesNotExist:
#             pass
    
#     elif event['type'] == 'payment_intent.payment_failed':
#         payment_intent = event['data']['object']
#         order_id = payment_intent['metadata']['order_id']
        
#         try:
#             order = Order.objects.get(id=order_id)
#             order.payment_status = 'failed'
#             order.save()
#         except Order.DoesNotExist:
#             pass
    
#     return HttpResponse(status=200)





# Set Stripe API key
if hasattr(settings, 'STRIPE_SECRET_KEY'):
    stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def process_payment_view(request, order_id):
    """Initial payment processing page - shows payment options"""
    order = get_object_or_404(Order, id=order_id, user=request.user, payment_status='pending')
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'credit_card')
        
        if payment_method == 'credit_card':
            # Check if Stripe is configured
            if not hasattr(settings, 'STRIPE_SECRET_KEY') or not settings.STRIPE_SECRET_KEY:
                messages.error(request, 'Payment processing is not configured. Please contact support.')
                return redirect('orders:order_detail', order_id=order.id)
            
            try:
                # Create Stripe Payment Intent
                intent = stripe.PaymentIntent.create(
                    amount=int(order.total * 100),  # Stripe uses cents
                    currency='usd',
                    metadata={
                        'order_id': str(order.id),
                        'order_number': order.order_number,
                    }
                )
                
                context = {
                    'order': order,
                    'client_secret': intent.client_secret,
                    'stripe_publishable_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', ''),
                }
                return render(request, 'payments/payment.html', context)
                
            except stripe.error.StripeError as e:
                messages.error(request, f'Payment setup error: {str(e)}')
                return redirect('orders:order_detail', order_id=order.id)
            except Exception as e:
                messages.error(request, 'An error occurred setting up payment. Please try again.')
                return redirect('orders:order_detail', order_id=order.id)
        
        elif payment_method == 'paypal':
            messages.info(request, 'PayPal payment is coming soon. Please use credit card payment.')
            return redirect('payments:process_payment', order_id=order.id)
        
        else:
            messages.error(request, 'Invalid payment method selected.')
            return redirect('payments:process_payment', order_id=order.id)
    
    # GET request - show payment options
    context = {
        'order': order,
        'stripe_publishable_key': getattr(settings, 'STRIPE_PUBLISHABLE_KEY', ''),
    }
    return render(request, 'payments/process_payment.html', context)

@login_required
def payment_success_view(request, order_id):
    """Payment success page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Update order status if payment completed
    if order.payment_status == 'completed' and order.status == 'pending':
        order.status = 'processing'
        order.save()
    
    messages.success(request, f'Payment successful! Your order {order.order_number} has been placed.')
    
    context = {'order': order}
    return render(request, 'payments/payment_success.html', context)

@login_required
def payment_cancel_view(request, order_id):
    """Payment cancellation page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    messages.warning(request, 'Payment was cancelled. You can try again anytime.')
    return redirect('orders:order_detail', order_id=order.id)

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
    
    try:
        if endpoint_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        else:
            event = json.loads(payload)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata'].get('order_id')
        
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.payment_status = 'completed'
                order.status = 'processing'
                order.payment_id = payment_intent['id']
                order.payment_method = 'stripe'
                order.save()
            except Order.DoesNotExist:
                pass
    
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata'].get('order_id')
        
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.payment_status = 'failed'
                order.save()
            except Order.DoesNotExist:
                pass
    
    return HttpResponse(status=200)

# Alternative simple payment view (if Stripe is not configured)
@login_required
def simple_payment_view(request, order_id):
    """Simple payment simulation for development/testing"""
    order = get_object_or_404(Order, id=order_id, user=request.user, payment_status='pending')
    
    if request.method == 'POST':
        # Simulate payment success
        order.payment_status = 'completed'
        order.status = 'processing'
        order.payment_method = 'test'
        order.save()
        
        messages.success(request, f'Payment simulated successfully! Order {order.order_number} is being processed.')
        return redirect('payments:payment_success', order_id=order.id)
    
    context = {'order': order}
    return render(request, 'payments/simple_payment.html', context)










