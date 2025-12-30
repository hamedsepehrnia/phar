"""
Admin برای اپ catalog
"""
from decimal import Decimal
from django.contrib import admin
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import path
from django.utils.html import format_html
from django import forms
from mptt.admin import DraggableMPTTAdmin
from apps.core.admin_utils import jalali_date
from .models import (
    Category, Brand, Product, ProductImage,
    ProductAttribute, ProductAttributeValue, Wishlist
)


class BulkPriceChangeForm(forms.Form):
    """فرم تغییر قیمت گروهی"""
    FILTER_CHOICES = [
        ('all', 'همه محصولات'),
        ('brand', 'بر اساس برند'),
        ('category', 'بر اساس دسته‌بندی'),
    ]
    ACTION_CHOICES = [
        ('increase', 'افزایش قیمت'),
        ('decrease', 'کاهش قیمت'),
    ]
    
    filter_type = forms.ChoiceField(
        choices=FILTER_CHOICES, 
        label='فیلتر بر اساس',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'filter_type'})
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.filter(is_active=True),
        required=False,
        label='برند',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'brand_select'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        label='دسته‌بندی',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'category_select'})
    )
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        label='نوع عملیات',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    percentage = forms.DecimalField(
        min_value=0,
        max_value=100,
        label='درصد تغییر',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثال: 10'})
    )


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    """مدیریت دسته‌بندی‌ها با drag & drop"""
    
    list_display = [
        'tree_actions',
        'indented_title',
        'is_active',
        'sort_order',
        'product_count',
        'created_at_jalali'
    ]
    list_display_links = ['indented_title']
    list_filter = ['is_active', 'level']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'sort_order']
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'slug', 'parent', 'image', 'description')
        }),
        ('وضعیت', {
            'fields': ('is_active', 'sort_order')
        }),
        ('سئو', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'تعداد محصول'
    
    def created_at_jalali(self, obj):
        return jalali_date(obj.created_at)
    created_at_jalali.short_description = 'تاریخ ایجاد'
    created_at_jalali.admin_order_field = 'created_at'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """مدیریت برندها"""
    
    list_display = ['name', 'country', 'is_active', 'product_count', 'logo_preview']
    list_filter = ['is_active', 'country']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'تعداد محصول'
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="40" height="40" style="object-fit: contain;"/>',
                obj.logo.url
            )
        return '-'
    logo_preview.short_description = 'لوگو'


class ProductImageInline(admin.TabularInline):
    """تصاویر محصول به صورت inline"""
    
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_main', 'sort_order']


class ProductAttributeValueInline(admin.TabularInline):
    """ویژگی‌های محصول به صورت inline"""
    
    model = ProductAttributeValue
    extra = 1
    autocomplete_fields = ['attribute']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """مدیریت محصولات"""
    
    list_display = [
        'name', 'sku', 'category', 'brand', 'price',
        'stock_quantity', 'is_in_stock', 'is_active',
        'prescription_required', 'image_preview'
    ]
    list_filter = [
        'is_active', 'is_in_stock', 'prescription_required',
        'category', 'brand', 'created_at'
    ]
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ['category', 'brand']
    list_editable = ['is_active', 'stock_quantity']
    date_hierarchy = 'created_at'
    inlines = [ProductImageInline, ProductAttributeValueInline]
    change_list_template = 'admin/catalog/product/change_list.html'
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': (
                'name', 'slug', 'description', 'short_description',
                'category', 'brand'
            )
        }),
        ('قیمت و موجودی', {
            'fields': (
                'price', 'compare_at_price', 'sku',
                'stock_quantity', 'is_in_stock', 'is_active'
            )
        }),
        ('اطلاعات دارویی', {
            'fields': (
                'prescription_required', 'expiry_date',
                'batch_number', 'max_purchase_per_user'
            ),
            'classes': ('collapse',)
        }),
        ('سئو', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('آمار', {
            'fields': ('view_count', 'sales_count'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['view_count', 'sales_count']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-price-change/', self.admin_site.admin_view(self.bulk_price_change_view), name='catalog_product_bulk_price_change'),
        ]
        return custom_urls + urls
    
    def bulk_price_change_view(self, request):
        """ویو تغییر قیمت گروهی"""
        if request.method == 'POST':
            form = BulkPriceChangeForm(request.POST)
            if form.is_valid():
                filter_type = form.cleaned_data['filter_type']
                brand = form.cleaned_data['brand']
                category = form.cleaned_data['category']
                action = form.cleaned_data['action']
                percentage = form.cleaned_data['percentage']
                
                # فیلتر محصولات
                products = Product.objects.filter(is_active=True)
                
                if filter_type == 'brand' and brand:
                    products = products.filter(brand=brand)
                elif filter_type == 'category' and category:
                    descendants = category.get_descendants(include_self=True)
                    products = products.filter(category__in=descendants)
                
                # اعمال تغییر قیمت
                count = 0
                for product in products:
                    old_price = product.price
                    change_amount = old_price * (percentage / Decimal('100'))
                    
                    if action == 'increase':
                        new_price = old_price + change_amount
                    else:
                        new_price = old_price - change_amount
                        if new_price < 0:
                            new_price = Decimal('0')
                    
                    product.price = new_price.quantize(Decimal('1'))
                    product.save(update_fields=['price'])
                    count += 1
                
                action_text = 'افزایش' if action == 'increase' else 'کاهش'
                messages.success(
                    request,
                    f'قیمت {count} محصول با {action_text} {percentage}% بروزرسانی شد.'
                )
                return redirect('admin:catalog_product_changelist')
        else:
            form = BulkPriceChangeForm()
        
        context = {
            'form': form,
            'title': 'تغییر قیمت گروهی محصولات',
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
        }
        return render(request, 'admin/catalog/product/bulk_price_change.html', context)
    
    def image_preview(self, obj):
        image = obj.main_image
        if image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;"/>',
                image.image.url
            )
        return '-'
    image_preview.short_description = 'تصویر'


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    """مدیریت ویژگی‌ها"""
    
    list_display = ['name', 'value_count']
    search_fields = ['name']
    
    def value_count(self, obj):
        return obj.values.count()
    value_count.short_description = 'تعداد استفاده'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """مدیریت علاقه‌مندی‌ها"""
    
    list_display = ['user', 'product', 'created_at_jalali']
    list_filter = ['created_at']
    search_fields = ['user__phone', 'product__name']
    raw_id_fields = ['user', 'product']
    date_hierarchy = 'created_at'
    
    def created_at_jalali(self, obj):
        return jalali_date(obj.created_at)
    created_at_jalali.short_description = 'تاریخ افزودن'
    created_at_jalali.admin_order_field = 'created_at'
