"""
Admin برای اپ cart
"""
from django.contrib import admin
from .models import Coupon, CouponUsage, Cart, CartItem


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """مدیریت کدهای تخفیف"""
    
    list_display = [
        'code', 'discount_type', 'discount_value', 
        'used_count', 'usage_limit', 'is_active',
        'valid_from', 'valid_until'
    ]
    list_filter = ['is_active', 'discount_type', 'valid_from', 'valid_until']
    search_fields = ['code']
    list_editable = ['is_active']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('code', 'is_active')
        }),
        ('تخفیف', {
            'fields': ('discount_type', 'discount_value', 'min_purchase', 'max_discount')
        }),
        ('محدودیت‌ها', {
            'fields': ('usage_limit', 'usage_limit_per_user', 'used_count')
        }),
        ('اعتبار', {
            'fields': ('valid_from', 'valid_until')
        }),
    )
    
    readonly_fields = ['used_count']


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    """سوابق استفاده از کد تخفیف"""
    
    list_display = ['coupon', 'user', 'discount_amount', 'order', 'used_at']
    list_filter = ['used_at', 'coupon']
    search_fields = ['coupon__code', 'user__phone']
    raw_id_fields = ['user', 'order']
    date_hierarchy = 'used_at'


class CartItemInline(admin.TabularInline):
    """آیتم‌های سبد به صورت inline"""
    
    model = CartItem
    extra = 0
    raw_id_fields = ['product']
    readonly_fields = ['price_snapshot']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """مدیریت سبدهای خرید"""
    
    list_display = ['id', 'user', 'session_key_short', 'items_count', 'total', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['user__phone', 'session_key']
    raw_id_fields = ['user', 'coupon']
    inlines = [CartItemInline]
    
    def session_key_short(self, obj):
        if obj.session_key:
            return obj.session_key[:10] + '...'
        return '-'
    session_key_short.short_description = 'کلید نشست'
    
    def items_count(self, obj):
        return obj.items_count
    items_count.short_description = 'تعداد آیتم'
    
    def total(self, obj):
        return f'{obj.total:,} تومان'
    total.short_description = 'جمع کل'
