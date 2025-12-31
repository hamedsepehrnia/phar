from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.catalog.models import Product, Category, Brand


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['core:home', 'core:about', 'core:contact', 'catalog:shop']

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    """Sitemap for products"""
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        return Product.objects.filter(is_active=True, stock__gt=0)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('catalog:product_detail', args=[obj.slug])


class CategorySitemap(Sitemap):
    """Sitemap for categories"""
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Category.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else None

    def location(self, obj):
        return f"{reverse('catalog:shop')}?category={obj.slug}"


class BrandSitemap(Sitemap):
    """Sitemap for brands"""
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Brand.objects.filter(is_active=True)

    def location(self, obj):
        return f"{reverse('catalog:shop')}?brand={obj.slug}"
