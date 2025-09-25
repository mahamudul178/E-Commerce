from django.shortcuts import render

# Create your views here.
# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Cart, CartItem
from .utils import get_or_create_cart


from decimal import Decimal

def cart_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.all() if cart else []
    
    # Calculate totals
    if cart:
        subtotal = cart.get_total_price()
        shipping_cost = Decimal('10.00')
        tax_rate = Decimal('0.08')
        tax_amount = subtotal * tax_rate
        total = subtotal + shipping_cost + tax_amount
    else:
        subtotal = Decimal('0.00')
        shipping_cost = Decimal('0.00')
        tax_amount = Decimal('0.00')
        total = Decimal('0.00')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'tax_amount': tax_amount,
        'total': total,
        'tax_rate_percent': 8,  # For display purposes
    }
    return render(request, 'cart/cart.html', context)

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0 or quantity > product.stock:
        messages.error(request, 'Invalid quantity.')
        return redirect('products:product_detail', slug=product.slug)
    
    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            messages.error(request, f'Only {product.stock} items available in stock.')
            return redirect('products:product_detail', slug=product.slug)
        cart_item.quantity = new_quantity
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart.')
    
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart.',
            'cart_count': cart.get_total_items()
        })
    
    return redirect('cart:cart_detail')

@require_POST
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = get_or_create_cart(request)
    
    # Ensure the cart item belongs to the current cart
    if cart_item.cart != cart:
        messages.error(request, 'Invalid request.')
        return redirect('cart:cart_detail')
    
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
    elif quantity > cart_item.product.stock:
        messages.error(request, f'Only {cart_item.product.stock} items available.')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated.')
    
    return redirect('cart:cart_detail')

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = get_or_create_cart(request)
    
    if cart_item.cart == cart:
        product_name = cart_item.product.name
        cart_item.delete()
        messages.success(request, f'{product_name} removed from cart.')
    
    return redirect('cart:cart_detail')

def clear_cart(request):
    cart = get_or_create_cart(request)
    if cart:
        cart.items.all().delete()
        messages.success(request, 'Cart cleared.')
    return redirect('cart:cart_detail')