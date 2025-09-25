# cart/context_processors.py - UPDATED VERSION
from decimal import Decimal
from .utils import get_or_create_cart

def cart_context(request):
    """Add cart information to all templates with proper calculations"""
    cart = get_or_create_cart(request)
    
    if cart and cart.items.exists():
        cart_total_items = cart.get_total_items()
        cart_total_price = cart.get_total_price()
        
        # Calculate additional values for checkout/cart pages
        shipping_cost = Decimal('10.00')
        tax_rate = Decimal('0.08')
        tax_amount = cart_total_price * tax_rate
        grand_total = cart_total_price + shipping_cost + tax_amount
    else:
        cart_total_items = 0
        cart_total_price = Decimal('0.00')
        shipping_cost = Decimal('0.00')
        tax_amount = Decimal('0.00')
        grand_total = Decimal('0.00')
    
    return {
        'cart': cart,
        'cart_total_items': cart_total_items,
        'cart_total_price': cart_total_price,
        'cart_shipping_cost': shipping_cost,
        'cart_tax_amount': tax_amount,
        'cart_grand_total': grand_total,
    }