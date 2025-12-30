"""
URLهای اپ catalog
"""
from django.urls import path, re_path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.ShopView.as_view(), name='shop'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('search/suggest/', views.SearchSuggestView.as_view(), name='search_suggest'),
    
    # دسته‌بندی - پشتیبانی از اسلاگ‌های فارسی
    re_path(r'^category/(?P<slug>[^/]+)/$', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # برند - پشتیبانی از اسلاگ‌های فارسی
    re_path(r'^brand/(?P<slug>[^/]+)/$', views.BrandDetailView.as_view(), name='brand_detail'),
    
    # محصول - پشتیبانی کامل از اسلاگ‌های فارسی
    re_path(r'^product/(?P<slug>[^/]+)/$', views.ProductDetailView.as_view(), name='product_detail'),
    
    # علاقه‌مندی‌ها
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('wishlist/toggle/<int:product_id>/', views.WishlistToggleView.as_view(), name='wishlist_toggle'),
]
