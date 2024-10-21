# context_processors.py
from .models import Cart,CartItem

def cart_count(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(cart_user=request.user)
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
            return {'cart_count': cart_items.count()}
        except Cart.DoesNotExist:
            return {'cart_count': 0}  # Return 0 if no cart exists for the user
    else:
        return {'cart_count': 0}  # Return 0 for anonymous users or when the user is not logged in
