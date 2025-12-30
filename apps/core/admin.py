"""
Admin برای اپ core
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import SiteSettings, Slider, Banner, Page, ContactMessage, FAQ


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """تنظیمات سایت"""
    
    fieldsets = (
        ('اطلاعات کلی', {
            'fields': ('site_name', 'site_description', 'logo', 'favicon')
        }),
        ('اطلاعات تماس', {
            'fields': ('phone', 'phone_2', 'email', 'address')
        }),
        ('شبکه‌های اجتماعی', {
            'fields': ('instagram', 'telegram', 'whatsapp')
        }),
        ('فوتر', {
            'fields': ('footer_text', 'copyright_text')
        }),
        ('سئو', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # فقط یک رکورد مجاز است
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    """اسلایدر"""
    
    list_display = ['title', 'image_preview', 'is_active', 'sort_order']
    list_filter = ['is_active']
    list_editable = ['is_active', 'sort_order']
    
    fieldsets = (
        ('اطلاعات کلی', {
            'fields': ('title', 'subtitle', 'button_text', 'link')
        }),
        ('تصویر', {
            'fields': ('image',),
            'description': 'سایز بهینه تصویر: 1024x214 پیکسل (نسبت 4.8:1) - فرمت: JPG یا PNG'
        }),
        ('تنظیمات', {
            'fields': ('is_active', 'sort_order')
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="50" style="object-fit: cover;"/>',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'تصویر'


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    """بنر"""
    
    list_display = ['title', 'position', 'image_preview', 'is_active', 'sort_order']
    list_filter = ['is_active', 'position']
    list_editable = ['is_active', 'sort_order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="50" style="object-fit: cover;"/>',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'تصویر'


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """صفحات ایستا"""
    
    list_display = ['title', 'slug', 'is_active', 'show_in_footer', 'updated_at']
    list_filter = ['is_active', 'show_in_footer']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active', 'show_in_footer']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """پیام‌های تماس"""
    
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at_jalali']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'created_at']
    date_hierarchy = 'created_at'
    
    def created_at_jalali(self, obj):
        from apps.core.admin_utils import jalali_date
        return jalali_date(obj.created_at)
    created_at_jalali.short_description = 'تاریخ ارسال'
    created_at_jalali.admin_order_field = 'created_at'
    
    def has_add_permission(self, request):
        return False


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """سوالات متداول"""
    
    list_display = ['question_short', 'is_active', 'sort_order']
    list_filter = ['is_active']
    list_editable = ['is_active', 'sort_order']
    
    def question_short(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_short.short_description = 'سوال'
