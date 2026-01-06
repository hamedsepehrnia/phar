"""
ویوهای اپ catalog
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.core.cache import cache
from django.conf import settings
from urllib.parse import unquote

from .models import Category, Product, Brand, Wishlist


class ShopView(ListView):
    """صفحه فروشگاه با لیست محصولات"""
    
    model = Product
    # TEMP: تست سرعت - برای برگشت به حالت اصلی این خط رو کامنت بزنید و خط بعدی رو آنکامنت کنید
    template_name = 'catalog/shop_minimal.html'
    # template_name = 'catalog/shop.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(
            is_active=True
        ).select_related(
            'category', 'brand'
        ).prefetch_related('images')
        
        # جستجو
        query = self.request.GET.get('q', '').strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(sku__icontains=query) |
                Q(brand__name__icontains=query)
            )
        
        # فیلتر بر اساس دسته‌بندی
        category_slug = self.request.GET.get('category')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug, is_active=True)
            descendants = category.get_descendants(include_self=True)
            queryset = queryset.filter(category__in=descendants)
        
        # فیلتر بر اساس برند
        brand_slug = self.request.GET.get('brand')
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)
        
        # فیلتر قیمت
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # فیلتر موجودی
        in_stock = self.request.GET.get('in_stock')
        if in_stock == '1':
            queryset = queryset.filter(is_in_stock=True)
        
        # مرتب‌سازی
        sort = self.request.GET.get('sort', 'newest')
        if sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'popular':
            queryset = queryset.order_by('-sales_count')
        elif sort == 'views':
            queryset = queryset.order_by('-view_count')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # دسته‌بندی‌ها با کش
        context['categories'] = self.get_cached_categories()
        
        # برندها
        context['brands'] = Brand.objects.filter(
            is_active=True
        ).annotate(
            product_count=Count('products')
        ).filter(product_count__gt=0)
        
        # فیلترهای فعال
        context['current_category'] = self.request.GET.get('category', '')
        context['current_brand'] = self.request.GET.get('brand', '')
        context['current_sort'] = self.request.GET.get('sort', 'newest')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['in_stock'] = self.request.GET.get('in_stock', '')
        context['query'] = self.request.GET.get('q', '')
        context['querystring'] = self.build_querystring()
        
        return context
    
    def get_cached_categories(self):
        """دریافت دسته‌بندی‌های اصلی با کش"""
        cache_key = 'active_root_categories'
        categories = cache.get(cache_key)
        
        if categories is None:
            # فقط دسته‌های اصلی (بدون والد)
            categories = Category.objects.filter(
                is_active=True,
                parent__isnull=True
            ).order_by('sort_order', 'name')
            cache.set(cache_key, categories, 60 * 10)  # 10 دقیقه
        
        return categories

    def build_querystring(self):
        """ساخت querystring بدون پارامتر صفحه برای استفاده در پیجینیشن"""
        params = self.request.GET.copy()
        params.pop('page', None)
        qs = params.urlencode()
        return f'&{qs}' if qs else ''


class CategoryDetailView(View):
    """صفحه جزئیات دسته‌بندی"""
    
    template_name = 'catalog/category_detail.html'
    
    def get(self, request, slug):
        # URL decode کردن اسلاگ برای پشتیبانی از کاراکترهای فارسی
        decoded_slug = unquote(slug)
        
        category = get_object_or_404(
            Category.objects.select_related('parent'),
            slug=decoded_slug,
            is_active=True
        )
        
        # محصولات این دسته و زیردسته‌ها
        descendants = category.get_descendants(include_self=True)
        products = Product.objects.filter(
            category__in=descendants,
            is_active=True
        ).select_related('category', 'brand').prefetch_related('images')
        
        # فیلتر و مرتب‌سازی
        sort = request.GET.get('sort', 'newest')
        if sort == 'newest':
            products = products.order_by('-created_at')
        elif sort == 'price_low':
            products = products.order_by('price')
        elif sort == 'price_high':
            products = products.order_by('-price')
        elif sort == 'popular':
            products = products.order_by('-sales_count')
        
        # صفحه‌بندی
        paginator = Paginator(products, 12)
        page = request.GET.get('page', 1)
        products = paginator.get_page(page)
        
        # Breadcrumb
        ancestors = category.get_ancestors(include_self=True)
        
        context = {
            'category': category,
            'products': products,
            'ancestors': ancestors,
            'subcategories': category.get_children().filter(is_active=True),
            'current_sort': sort,
        }
        
        return render(request, self.template_name, context)


class ProductDetailView(View):
    """صفحه جزئیات محصول"""
    
    # TEMP: تست سرعت - برای برگشت به حالت اصلی این خط رو کامنت بزنید و خط بعدی رو آنکامنت کنید
    template_name = 'catalog/product_minimal.html'
    # template_name = 'catalog/product_detail.html'
    
    def get(self, request, slug):
        # URL decode کردن اسلاگ برای پشتیبانی از کاراکترهای فارسی
        decoded_slug = unquote(slug)
        
        product = get_object_or_404(
            Product.objects.filter(
                is_active=True
            ).select_related(
                'category', 'brand'
            ).prefetch_related(
                'images', 'attribute_values__attribute'
            ),
            slug=decoded_slug
        )
        
        # افزایش شمارنده بازدید
        Product.objects.filter(pk=product.pk).update(
            view_count=product.view_count + 1
        )
        
        # Breadcrumb
        ancestors = product.category.get_ancestors(include_self=True)
        
        # محصولات مرتبط
        related_products = product.get_related_products()
        
        # بررسی علاقه‌مندی
        is_in_wishlist = False
        if request.user.is_authenticated:
            is_in_wishlist = Wishlist.objects.filter(
                user=request.user,
                product=product
            ).exists()
        
        context = {
            'product': product,
            'ancestors': ancestors,
            'related_products': related_products,
            'is_in_wishlist': is_in_wishlist,
        }
        
        return render(request, self.template_name, context)


class SearchView(View):
    """جستجوی محصولات"""
    
    template_name = 'catalog/search.html'
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        products = Product.objects.none()
        
        if query:
            products = Product.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(sku__icontains=query) |
                Q(brand__name__icontains=query),
                is_active=True
            ).select_related('category', 'brand').prefetch_related('images')
        
        # صفحه‌بندی
        paginator = Paginator(products, 12)
        page = request.GET.get('page', 1)
        products = paginator.get_page(page)
        
        context = {
            'query': query,
            'products': products,
        }
        
        return render(request, self.template_name, context)


class SearchSuggestView(View):
    """پیشنهاد جستجو (Ajax)"""
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse({'results': []})
        
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(sku__icontains=query),
            is_active=True
        ).select_related('brand').prefetch_related('images')[:5]
        
        results = []
        for product in products:
            image_url = ''
            if product.main_image:
                image_url = product.main_image.image.url
            
            results.append({
                'name': product.name,
                'url': product.get_absolute_url(),
                'image': image_url,
                'price': str(product.price),
            })
        
        return JsonResponse({'results': results})


class WishlistView(LoginRequiredMixin, View):
    """لیست علاقه‌مندی‌ها"""
    
    template_name = 'catalog/wishlist.html'
    
    def get(self, request):
        wishlist = Wishlist.objects.filter(
            user=request.user
        ).select_related('product__category', 'product__brand').prefetch_related('product__images')
        
        return render(request, self.template_name, {'wishlist': wishlist})


class WishlistToggleView(LoginRequiredMixin, View):
    """افزودن/حذف از علاقه‌مندی‌ها"""
    
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if created:
            message = 'محصول به علاقه‌مندی‌ها اضافه شد'
            added = True
        else:
            wishlist_item.delete()
            message = 'محصول از علاقه‌مندی‌ها حذف شد'
            added = False
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'added': added,
                'message': message
            })
        
        messages.success(request, message)
        return redirect(request.META.get('HTTP_REFERER', 'catalog:shop'))


class BrandDetailView(View):
    """صفحه برند"""
    
    template_name = 'catalog/brand_detail.html'
    
    def get(self, request, slug):
        # URL decode کردن اسلاگ برای پشتیبانی از کاراکترهای فارسی
        decoded_slug = unquote(slug)
        
        brand = get_object_or_404(Brand, slug=decoded_slug, is_active=True)
        
        products = Product.objects.filter(
            brand=brand,
            is_active=True
        ).select_related('category').prefetch_related('images')
        
        # مرتب‌سازی
        sort = request.GET.get('sort', 'newest')
        if sort == 'newest':
            products = products.order_by('-created_at')
        elif sort == 'price_low':
            products = products.order_by('price')
        elif sort == 'price_high':
            products = products.order_by('-price')
        
        # صفحه‌بندی
        paginator = Paginator(products, 12)
        page = request.GET.get('page', 1)
        products = paginator.get_page(page)
        
        context = {
            'brand': brand,
            'products': products,
            'current_sort': sort,
        }
        
        return render(request, self.template_name, context)
