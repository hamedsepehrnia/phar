"""
Admin برای اپ orders
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.core.admin_utils import jalali_date
from .models import Order, OrderItem, PaymentTransaction, ShippingMethod


class OrderItemInline(admin.TabularInline):
    """آیتم‌های سفارش"""
    
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_sku', 'price', 'quantity', 'total_price']
    raw_id_fields = ['product']
    
    def total_price(self, obj):
        if obj.total_price:
            return f'{obj.total_price:,} تومان'
        return '-'
    total_price.short_description = 'جمع'


class PaymentInline(admin.TabularInline):
    """تراکنش‌های پرداخت"""
    
    model = PaymentTransaction
    extra = 0
    readonly_fields = ['amount', 'status', 'gateway', 'ref_id', 'created_at_jalali']
    
    def created_at_jalali(self, obj):
        return jalali_date(obj.created_at)
    created_at_jalali.short_description = 'تاریخ ایجاد'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """مدیریت سفارشات"""
    
    list_display = [
        'product_names', 'user', 'status_badge', 'total_formatted',
        'receiver_name', 'address_city', 'created_at_jalali'
    ]
    list_filter = ['status', 'created_at', 'address_province']
    search_fields = ['order_number', 'user__phone', 'receiver_name', 'receiver_phone']
    date_hierarchy = 'created_at'
    raw_id_fields = ['user']
    inlines = [OrderItemInline, PaymentInline]
    readonly_fields = [
        'order_number', 'user', 'subtotal', 'shipping_cost',
        'discount_amount', 'coupon_code', 'total',
        'created_at_jalali_display', 'updated_at_jalali_display', 'paid_at_jalali_display'
    ]
    
    fieldsets = (
        ('اطلاعات سفارش', {
            'fields': ('order_number', 'user', 'status')
        }),
        ('آدرس', {
            'fields': (
                'address_title', 'address_province', 'address_city',
                'address_full', 'address_postal_code',
                'receiver_name', 'receiver_phone'
            )
        }),
        ('مبالغ', {
            'fields': (
                'subtotal', 'shipping_cost', 'discount_amount',
                'coupon_code', 'total'
            )
        }),
        ('ارسال', {
            'fields': ('shipping_method', 'tracking_code')
        }),
        ('یادداشت‌ها', {
            'fields': ('note', 'admin_note'),
            'classes': ('collapse',)
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at_jalali_display', 'paid_at_jalali_display'),
            'classes': ('collapse',)
        }),
    )
    
    def product_names(self, obj):
        """نمایش نام محصولات سفارش"""
        items = obj.items.all()[:2]
        names = [item.product_name for item in items]
        if obj.items.count() > 2:
            return f"{', '.join(names)} و {obj.items.count() - 2} کالای دیگر"
        return ', '.join(names) if names else '-'
    product_names.short_description = 'محصولات'
    
    def created_at_jalali(self, obj):
        return jalali_date(obj.created_at)
    created_at_jalali.short_description = 'تاریخ ثبت'
    created_at_jalali.admin_order_field = 'created_at'
    
    def created_at_jalali_display(self, obj):
        return jalali_date(obj.created_at)
    created_at_jalali_display.short_description = 'تاریخ ایجاد'
    
    def updated_at_jalali_display(self, obj):
        return jalali_date(obj.updated_at)
    updated_at_jalali_display.short_description = 'تاریخ بروزرسانی'
    
    def paid_at_jalali_display(self, obj):
        return jalali_date(obj.paid_at)
    paid_at_jalali_display.short_description = 'تاریخ پرداخت'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'warning',
            'paid': 'info',
            'processing': 'primary',
            'shipped': 'secondary',
            'delivered': 'success',
            'canceled': 'danger',
            'returned': 'dark',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span style="padding: 3px 10px; border-radius: 4px; '
            'background-color: var(--{}-bg); color: var(--{});">{}</span>',
            color, color, obj.status_display
        )
    status_badge.short_description = 'وضعیت'
    
    def total_formatted(self, obj):
        return f'{obj.total:,} تومان'
    total_formatted.short_description = 'مبلغ'


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    """مدیریت تراکنش‌ها"""
    
    list_display = ['order', 'amount_formatted', 'status', 'gateway', 'ref_id', 'created_at_jalali']
    list_filter = ['status', 'gateway', 'created_at']
    search_fields = ['order__order_number', 'ref_id', 'authority']
    raw_id_fields = ['order']
    readonly_fields = ['order', 'amount', 'gateway', 'authority', 'ref_id', 'card_number', 'created_at_jalali_display']
    
    def amount_formatted(self, obj):
        return f'{obj.amount:,} تومان'
    amount_formatted.short_description = 'مبلغ'
    
    def created_at_jalali(self, obj):
        return jalali_date(obj.created_at)
    created_at_jalali.short_description = 'تاریخ ایجاد'
    created_at_jalali.admin_order_field = 'created_at'
    
    def created_at_jalali_display(self, obj):
        return jalali_date(obj.created_at)
    created_at_jalali_display.short_description = 'تاریخ ایجاد'


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    """مدیریت روش‌های ارسال"""
    
    list_display = ['name', 'price_formatted', 'delivery_estimate', 'is_active', 'sort_order']
    list_filter = ['is_active']
    list_editable = ['is_active', 'sort_order']
    
    def price_formatted(self, obj):
        return f'{obj.price:,} تومان'
    price_formatted.short_description = 'هزینه'
