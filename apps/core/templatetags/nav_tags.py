"""
Template tags برای navigation
"""
from django import template
from django.urls import reverse, resolve

register = template.Library()


@register.simple_tag(takes_context=True)
def is_active_menu(context, url_name, *args, **kwargs):
    """
    بررسی اینکه آیا menu item فعلی active است یا نه
    """
    request = context.get('request')
    if not request:
        return ''
    
    # بررسی URL name
    current_url_name = request.resolver_match.url_name if request.resolver_match else None
    if current_url_name == url_name:
        return 'active'
    
    # بررسی namespace
    if hasattr(request.resolver_match, 'namespace'):
        current_namespace = request.resolver_match.namespace
        if url_name in ['shop', 'product_detail', 'category_detail'] and current_namespace == 'catalog':
            return 'active'
    
    return ''


@register.simple_tag(takes_context=True) 
def menu_active_class(context, url_name, css_class='active', *args, **kwargs):
    """
    برگرداندن کلاس CSS برای menu item active
    """
    if is_active_menu(context, url_name, *args, **kwargs):
        return css_class
    return ''


@register.simple_tag(takes_context=True)
def is_catalog_active(context):
    """
    بررسی اینکه آیا در بخش کاتالوگ هستیم یا نه
    """
    request = context.get('request')
    if not request or not request.resolver_match:
        return False
        
    # بررسی namespace
    if request.resolver_match.namespace == 'catalog':
        return True
        
    # بررسی URL name های مرتبط با کاتالوگ
    catalog_urls = ['shop', 'search', 'product_detail', 'category_detail', 'brand_detail', 'wishlist']
    if request.resolver_match.url_name in catalog_urls:
        return True
        
    return False


@register.simple_tag(takes_context=True)
def active_sort_filter(context, sort_type):
    """
    بررسی اینکه آیا filter sorting فعلی active است
    """
    request = context.get('request')
    if not request:
        return False
        
    current_sort = request.GET.get('sort', 'newest')
    return current_sort == sort_type


@register.simple_tag(takes_context=True)
def nav_item_classes(context, url_name, sort_type=None):
    """
    کلاس‌های کامل برای nav item
    """
    request = context.get('request')
    if not request:
        return 'text-gray-600'
    
    # بررسی برای home page    
    if url_name == 'home' and request.resolver_match.url_name == 'home':
        return 'text-primary-800'
    
    # بررسی برای catalog pages
    if url_name == 'catalog' and is_catalog_active(context):
        return 'text-primary-800'
    
    # بررسی برای sort filters
    if sort_type and active_sort_filter(context, sort_type):
        return 'text-primary-800'
    
    # بررسی برای صفحات مشخص
    if request.resolver_match.url_name == url_name:
        return 'text-primary-800'
        
    return 'text-gray-600'