# cart/utils.py
from .models import Cart, CartItem

def get_or_create_cart(request):
    """Get or create cart for authenticated user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Migrate session cart to user cart if exists
        if not request.session.session_key:
            request.session.create()
        
        session_cart = Cart.objects.filter(session_key=request.session.session_key).first()
        if session_cart and session_cart != cart:
            # Merge session cart with user cart
            for item in session_cart.items.all():
                user_cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=item.product,
                    defaults={'quantity': item.quantity}
                )
                if not created:
                    user_cart_item.quantity += item.quantity
                    user_cart_item.save()
            
            session_cart.delete()
        
        return cart
    else:
        if not request.session.session_key:
            request.session.create()
        
        cart, created = Cart.objects.get_or_create(session_key=request.session.session_key)
        return cart