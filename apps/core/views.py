"""
ویوهای اپ core
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView, DetailView
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Count, Q
from django.http import Http404
from urllib.parse import unquote, quote
import logging

from .models import SiteSettings, Slider, Banner, Page, ContactMessage, FAQ
from .forms import ContactForm
from apps.catalog.models import Category, Product, Brand

logger = logging.getLogger(__name__)


class HomeView(View):
    """صفحه اصلی"""
    
    # TEMP: تست سرعت - برای برگشت به حالت اصلی این خط رو کامنت بزنید و خط بعدی رو آنکامنت کنید
    template_name = 'core/home_minimal.html'
    # template_name = 'core/home.html'
    
    def get(self, request):
        # اسلایدر
        sliders = Slider.objects.filter(is_active=True)
        
        # بنرها
        banners_top = Banner.objects.filter(is_active=True, position='home_top')
        banners_middle = Banner.objects.filter(is_active=True, position='home_middle')
        
        # دسته‌بندی‌های اصلی
        categories = Category.objects.filter(
            is_active=True,
            level=0
        ).prefetch_related('children')[:8]
        
        # محصولات جدید
        new_products = Product.objects.filter(
            is_active=True
        ).select_related(
            'category', 'brand'
        ).prefetch_related('images').order_by('-created_at')[:12]
        
        # محصولات پرفروش
        popular_products = Product.objects.filter(
            is_active=True
        ).select_related(
            'category', 'brand'
        ).prefetch_related('images').order_by('-sales_count')[:8]
        
        # محصولات تخفیف‌دار
        sale_products = Product.objects.filter(
            is_active=True,
            compare_at_price__isnull=False
        ).exclude(
            compare_at_price=0
        ).select_related(
            'category', 'brand'
        ).prefetch_related('images')[:8]
        
        # برندهای محبوب
        brands = Brand.objects.filter(
            is_active=True
        ).annotate(
            product_count=Count('products')
        ).filter(product_count__gt=0).order_by('-product_count')[:12]
        
        context = {
            'sliders': sliders,
            'banners_top': banners_top,
            'banners_middle': banners_middle,
            'categories': categories,
            'new_products': new_products,
            'popular_products': popular_products,
            'sale_products': sale_products,
            'brands': brands,
        }
        
        return render(request, self.template_name, context)


class AboutView(TemplateView):
    """صفحه درباره ما"""
    
    template_name = 'core/about.html'


class ContactView(View):
    """صفحه تماس با ما"""
    
    template_name = 'core/contact.html'
    
    def get(self, request):
        form = ContactForm()
        settings = SiteSettings.get_settings()
        
        context = {
            'form': form,
            'settings': settings,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = ContactForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'پیام شما با موفقیت ارسال شد')
            return redirect('core:contact')
        
        settings = SiteSettings.get_settings()
        
        context = {
            'form': form,
            'settings': settings,
        }
        
        return render(request, self.template_name, context)


class PageDetailView(DetailView):
    """صفحات ایستا"""
    
    model = Page
    template_name = 'core/page.html'
    context_object_name = 'page'
    
    def get_queryset(self):
        return Page.objects.filter(is_active=True)


class FAQView(View):
    """سوالات متداول"""
    
    template_name = 'core/faq.html'
    
    def get(self, request):
        faqs = FAQ.objects.filter(is_active=True)
        
        return render(request, self.template_name, {'faqs': faqs})


def handler404(request, exception):
    """
    مدیریت کننده خطای 404 با پشتیبانی از اسلاگ‌های فارسی
    """
    # لاگ کردن URL که باعث 404 شده
    logger.warning(f"404 Error for URL: {request.path} - User: {request.user}")
    
    # بررسی اینکه آیا URL شامل کاراکترهای encode شده است
    if '%' in request.path:
        try:
            decoded_path = unquote(request.path)
            if decoded_path != request.path:
                # تلاش برای پیدا کردن صفحه با URL decode شده
                logger.info(f"Trying to redirect from {request.path} to {decoded_path}")
                return redirect(decoded_path, permanent=True)
        except:
            pass
    
    # اگر URL مربوط به محصول است، تلاش کن با روش‌های مختلف پیدایش کن
    if '/product/' in request.path:
        try:
            slug_part = request.path.split('/product/')[-1].rstrip('/')
            # تلاش با URL decode
            decoded_slug = unquote(slug_part)
            
            # جستجو با اسلاگ اصلی
            product = Product.objects.filter(
                Q(slug=slug_part) | Q(slug=decoded_slug),
                is_active=True
            ).first()
            
            if product:
                return redirect('catalog:product_detail', slug=product.slug)
            
        except Exception as e:
            logger.error(f"Error in 404 handler: {e}")
    
    # نمایش صفحه 404 معمولی
    context = {
        'request_path': request.path,
    }
    
    return render(request, '404.html', context, status=404)
