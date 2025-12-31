"""
تنظیمات سفارشی پنل ادمین
Custom Admin Configuration
"""
from django.contrib import admin
from django.contrib.admin.apps import AdminConfig


class CustomAdminSite(admin.AdminSite):
    """پنل ادمین سفارشی با ترتیب دلخواه اپ‌ها"""
    
    site_header = 'پنل مدیریت داروخانه دکتر واعظی'
    site_title = 'داروخانه دکتر واعظی'
    index_title = 'مدیریت سایت'
    
    def get_app_list(self, request, app_label=None):
        """
        سفارشی‌سازی ترتیب نمایش اپ‌ها در پنل ادمین
        """
        app_list = super().get_app_list(request, app_label)
        
        # ترتیب دلخواه اپ‌ها
        app_order = {
            'سفارشات': 1,
            'کاتالوگ محصولات': 2,
            'مدیریت کاربران': 3,
            'تنظیمات و صفحات': 4,
            'نظرات': 5,
            'سبد خرید': 6,
            'پنل کاربری': 7,
        }
        
        # مرتب‌سازی بر اساس ترتیب تعریف شده
        def sort_key(app):
            app_name = app.get('name', '')
            return app_order.get(app_name, 999)  # اپ‌های تعریف نشده در انتها
        
        sorted_app_list = sorted(app_list, key=sort_key)
        
        return sorted_app_list


# ایجاد نمونه سفارشی از admin site
custom_admin_site = CustomAdminSite(name='custom_admin')
