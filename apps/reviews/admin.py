"""
Admin برای اپ reviews
"""
from django.contrib import admin
from apps.core.admin_utils import jalali_date
from config.admin import custom_admin_site
from .models import Review


@admin.register(Review, site=custom_admin_site)
class ReviewAdmin(admin.ModelAdmin):
    """مدیریت نظرات"""
    
    list_display = ['user', 'product', 'rating', 'status', 'is_buyer', 'created_at_jalali']
    list_filter = ['status', 'rating', 'is_buyer', 'created_at']
    search_fields = ['user__phone', 'product__name', 'content']
    raw_id_fields = ['user', 'product']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    
    actions = ['approve_reviews', 'reject_reviews']
    
    def created_at_jalali(self, obj):
        return jalali_date(obj.created_at)
    created_at_jalali.short_description = 'تاریخ ثبت'
    created_at_jalali.admin_order_field = 'created_at'
    
    def approve_reviews(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f'{queryset.count()} نظر تایید شد')
    approve_reviews.short_description = 'تایید نظرات انتخاب شده'
    
    def reject_reviews(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f'{queryset.count()} نظر رد شد')
    reject_reviews.short_description = 'رد نظرات انتخاب شده'
