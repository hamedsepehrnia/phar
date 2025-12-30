"""
Context processor برای دسته‌بندی‌ها
"""
from django.core.cache import cache
from .models import Category


def categories_context(request):
    """اضافه کردن دسته‌بندی‌ها به تمام تمپلیت‌ها"""
    
    cache_key = 'navbar_categories'
    categories = cache.get(cache_key)
    
    if categories is None:
        categories = Category.objects.filter(
            is_active=True,
            level=0  # فقط دسته‌های ریشه
        ).prefetch_related(
            'children__children'  # زیردسته‌ها تا 2 سطح
        ).order_by('sort_order', 'name')
        
        cache.set(cache_key, list(categories), 60 * 10)  # 10 دقیقه
    
    return {'nav_categories': categories}
