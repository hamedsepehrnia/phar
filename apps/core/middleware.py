"""
Middleware برای پردازش URLs و پشتیبانی از کاراکترهای فارسی
"""
from urllib.parse import unquote
from django.http import HttpResponseNotFound
from django.shortcuts import redirect


class PersianSlugMiddleware:
    """
    Middleware برای پردازش اسلاگ‌های فارسی در URL
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # بررسی و decode کردن URL
        original_path = request.path
        decoded_path = unquote(original_path)
        
        # اگر URL decode شده متفاوت از اصلی باشد، path را به‌روزرسانی کن
        if decoded_path != original_path and not original_path.startswith('/admin/'):
            # بررسی اینکه آیا URL شامل کاراکترهای فارسی encode شده است
            if '%' in original_path:
                # ایجاد یک redirect permanent برای SEO
                return redirect(decoded_path, permanent=True)
        
        response = self.get_response(request)
        return response


class UnicodeURLMiddleware:
    """
    Middleware برای مدیریت بهتر URL های Unicode
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # تنظیم encoding مناسب برای URL
        if hasattr(request, 'path'):
            try:
                # اطمینان از اینکه path به درستی decode شده
                request.path = unquote(request.path)
            except UnicodeDecodeError:
                # در صورت خطا، path را همان‌طور که هست نگه دار
                pass
        
        response = self.get_response(request)
        
        # اضافه کردن هدر برای پشتیبانی از UTF-8
        if hasattr(response, 'charset'):
            response.charset = 'utf-8'
        
        return response