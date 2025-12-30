"""
Template tags برای دسته‌بندی درختی
"""
from django import template
from django.utils.safestring import mark_safe
from ..models import Category

register = template.Library()


@register.inclusion_tag('catalog/tags/category_tree.html')
def render_category_tree(categories=None, current_category=None):
    """رندر درخت دسته‌بندی به صورت UL/LI"""
    if categories is None:
        categories = Category.objects.filter(
            is_active=True,
            level=0
        ).prefetch_related('children__children')
    
    return {
        'categories': categories,
        'current_category': current_category,
    }


@register.inclusion_tag('catalog/tags/category_sidebar.html')
def render_category_sidebar(current_category=None):
    """رندر سایدبار دسته‌بندی"""
    categories = Category.objects.filter(
        is_active=True,
        level=0
    ).prefetch_related('children__children__children')
    
    return {
        'categories': categories,
        'current_category': current_category,
    }


@register.inclusion_tag('catalog/tags/breadcrumb.html')
def render_breadcrumb(obj):
    """رندر breadcrumb برای دسته یا محصول"""
    ancestors = []
    
    if hasattr(obj, 'get_ancestors'):
        # Category
        ancestors = list(obj.get_ancestors(include_self=True))
    elif hasattr(obj, 'category'):
        # Product
        ancestors = list(obj.category.get_ancestors(include_self=True))
    
    return {'ancestors': ancestors, 'current': obj}


@register.simple_tag
def category_product_count(category):
    """تعداد محصولات یک دسته (شامل زیردسته‌ها)"""
    descendants = category.get_descendants(include_self=True)
    from ..models import Product
    return Product.objects.filter(
        category__in=descendants,
        is_active=True
    ).count()


@register.filter
def format_price(value):
    """فرمت قیمت به صورت فارسی"""
    try:
        value = int(value)
        return '{:,}'.format(value).replace(',', '٫')
    except (ValueError, TypeError):
        return value


@register.simple_tag
def get_root_categories():
    """دریافت دسته‌بندی‌های اصلی (ریشه)"""
    return Category.objects.filter(
        is_active=True,
        level=0
    ).prefetch_related('children')


@register.simple_tag
def get_all_categories():
    """دریافت همه دسته‌بندی‌های فعال"""
    return Category.objects.filter(
        is_active=True
    ).select_related('parent')


@register.filter
def get_children(category):
    """دریافت زیردسته‌های یک دسته"""
    return category.get_children().filter(is_active=True)
