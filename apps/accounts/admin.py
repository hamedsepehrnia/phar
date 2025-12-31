"""
Admin برای اپ accounts
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.core.admin_utils import jalali_date
from config.admin import custom_admin_site
from .models import User, OTPCode, Address


@admin.register(User, site=custom_admin_site)
class UserAdmin(BaseUserAdmin):
    """پنل مدیریت کاربران"""
    
    list_display = ['phone', 'first_name', 'last_name', 'is_active', 'is_verified', 'date_joined_jalali']
    list_filter = ['is_active', 'is_verified', 'is_staff', 'gender', 'date_joined']
    search_fields = ['phone', 'first_name', 'last_name', 'national_code', 'email']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('اطلاعات ورود', {'fields': ('phone', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name', 'email', 'national_code', 'gender', 'birth_date', 'avatar')}),
        ('دسترسی‌ها', {'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('تاریخ‌ها', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    
    def date_joined_jalali(self, obj):
        return jalali_date(obj.date_joined)
    date_joined_jalali.short_description = 'تاریخ عضویت'
    date_joined_jalali.admin_order_field = 'date_joined'


@admin.register(OTPCode, site=custom_admin_site)
class OTPCodeAdmin(admin.ModelAdmin):
    """پنل مدیریت کدهای یکبار مصرف"""
    
    list_display = ['phone', 'code', 'created_at_jalali', 'is_used', 'attempts']
    list_filter = ['is_used', 'created_at']
    search_fields = ['phone']
    readonly_fields = ['phone', 'code', 'created_at', 'is_used', 'attempts']
    
    def created_at_jalali(self, obj):
        return jalali_date(obj.created_at)
    created_at_jalali.short_description = 'تاریخ ایجاد'
    created_at_jalali.admin_order_field = 'created_at'


@admin.register(Address, site=custom_admin_site)
class AddressAdmin(admin.ModelAdmin):
    """پنل مدیریت آدرس‌ها"""
    
    list_display = ['user', 'title', 'city', 'is_default', 'created_at_jalali']
    list_filter = ['is_default', 'province', 'city']
    search_fields = ['user__phone', 'address', 'receiver_name', 'receiver_phone']
    raw_id_fields = ['user']
    
    def created_at_jalali(self, obj):
        return jalali_date(obj.created_at)
    created_at_jalali.short_description = 'تاریخ ایجاد'
    created_at_jalali.admin_order_field = 'created_at'
