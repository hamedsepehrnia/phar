"""
Context processor برای سبد خرید
"""
from .models import Cart


def cart_context(request):
    """اضافه کردن سبد خرید به تمام تمپلیت‌ها"""
    
    cart = None
    cart_count = 0
    cart_total = 0
    
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key).first()
        
        if cart:
            cart_count = cart.items_count
            cart_total = cart.total
    except Exception:
        pass
    
    return {
        'cart': cart,
        'cart_count': cart_count,
        'cart_total': cart_total,
    }
