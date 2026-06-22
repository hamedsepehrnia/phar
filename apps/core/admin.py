"""
Admin برای اپ core
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.utils.html import format_html
from config.admin import custom_admin_site
from .models import SiteSettings, Slider, Banner, Page, ContactMessage, FAQ


@admin.register(SiteSettings, site=custom_admin_site)
class SiteSettingsAdmin(admin.ModelAdmin):
    """تنظیمات سایت"""

    def _db_columns(self):
        try:
            from django.db import connection
            table = SiteSettings._meta.db_table
            with connection.cursor() as cursor:
                return {
                    col.name
                    for col in connection.introspection.get_table_description(cursor, table)
                }
        except Exception:
            return {f.name for f in SiteSettings._meta.get_fields() if hasattr(f, 'column')}

    def _fields_if_exist(self, *names):
        columns = self._db_columns()
        return [name for name in names if name in columns]

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('اطلاعات کلی', {
                'fields': self._fields_if_exist('site_name', 'site_description', 'logo', 'favicon'),
            }),
            ('اطلاعات تماس', {
                'fields': self._fields_if_exist('phone', 'phone_2', 'email', 'address'),
            }),
        ]
        about_fields = self._fields_if_exist('about_short', 'about_content')
        if about_fields:
            fieldsets.append((
                'درباره ما',
                {
                    'fields': about_fields,
                    'description': 'اگر خالی باشد، متن پیش‌فرض سایت نمایش داده می‌شود.',
                },
            ))
        social_fields = self._fields_if_exist('instagram', 'telegram', 'whatsapp')
        if social_fields:
            fieldsets.append(('شبکه‌های اجتماعی', {'fields': social_fields}))
        map_fields = self._fields_if_exist('map_latitude', 'map_longitude', 'map_zoom')
        if map_fields:
            fieldsets.append(('نقشه و موقعیت', {'fields': map_fields}))
        footer_fields = self._fields_if_exist('footer_text', 'copyright_text')
        if footer_fields:
            fieldsets.append(('فوتر', {'fields': footer_fields}))
        seo_fields = self._fields_if_exist('meta_title', 'meta_description', 'meta_keywords')
        if seo_fields:
            fieldsets.append((
                'سئو',
                {'fields': seo_fields, 'classes': ('collapse',)},
            ))
        return [fs for fs in fieldsets if fs[1]['fields']]

    def changelist_view(self, request, extra_context=None):
        try:
            obj, _created = SiteSettings.objects.get_or_create(
                pk=1,
                defaults={'site_name': 'داروخانه دکتر واعظی'},
            )
            return redirect(f'{self.admin_site.name}:core_sitesettings_change', obj.pk)
        except Exception:
            return super().changelist_view(request, extra_context)

    def has_add_permission(self, request):
        try:
            return not SiteSettings.objects.exists()
        except Exception:
            return True
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Slider, site=custom_admin_site)
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


@admin.register(Banner, site=custom_admin_site)
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


@admin.register(Page, site=custom_admin_site)
class PageAdmin(admin.ModelAdmin):
    """صفحات ایستا"""
    
    list_display = ['title', 'slug', 'is_active', 'show_in_footer', 'updated_at']
    list_filter = ['is_active', 'show_in_footer']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active', 'show_in_footer']


@admin.register(ContactMessage, site=custom_admin_site)
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


@admin.register(FAQ, site=custom_admin_site)
class FAQAdmin(admin.ModelAdmin):
    """سوالات متداول"""
    
    list_display = ['question_short', 'is_active', 'sort_order']
    list_filter = ['is_active']
    list_editable = ['is_active', 'sort_order']
    
    def question_short(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
    question_short.short_description = 'سوال'
