from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def get_cart_count(context):
    """Get the total number of items in the cart."""
    request = context.get('request')
    if not request:
        return 0
    
    # Try to get cart from session or user
    from apps.cart.models import Cart
    
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        if not session_key:
            return 0
        cart = Cart.objects.filter(session_key=session_key).first()
    
    if cart:
        return cart.items.count()
    return 0


@register.simple_tag(takes_context=True)
def get_cart_total(context):
    """Get the total price of items in the cart."""
    request = context.get('request')
    if not request:
        return 0
    
    from apps.cart.models import Cart
    
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        if not session_key:
            return 0
        cart = Cart.objects.filter(session_key=session_key).first()
    
    if cart:
        return cart.get_total()
    return 0


@register.simple_tag(takes_context=True)
def get_cart(context):
    """Get the current cart object."""
    request = context.get('request')
    if not request:
        return None
    
    from apps.cart.models import Cart
    
    if request.user.is_authenticated:
        return Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        if not session_key:
            return None
        return Cart.objects.filter(session_key=session_key).first()


@register.filter
def multiply(value, arg):
    """Multiply value by arg."""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def format_price(value):
    """Format price with thousand separators."""
    try:
        return "{:,}".format(int(value))
    except (ValueError, TypeError):
        return value
