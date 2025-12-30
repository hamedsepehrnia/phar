from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('blog/', views.blog, name='blog'),
    path('blog/<int:post_id>/', views.blog_single, name='blog_single'),
    path('about-us/', views.about_us, name='about_us'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('login/', views.login, name='login'),
    path('login-otp/', views.login_otp, name='login_otp'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('account-info/', views.account_info, name='account_info'),
    path('orders/', views.orders, name='orders'),
    path('addresses/', views.addresses, name='addresses'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('shopping-cart/', views.shopping_cart, name='shopping_cart'),
    path('empty-shopping-cart/', views.empty_shopping_cart, name='empty_shopping_cart'),
    path('checkout-shipping/', views.checkout_shipping, name='checkout_shipping'),
    path('checkout-payment/', views.checkout_payment, name='checkout_payment'),
    path('success-payment/', views.success_payment, name='success_payment'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('messages/', views.messages, name='messages'),
    path('reviews/', views.reviews, name='reviews'),
    path('maintenance/', views.maintenance, name='maintenance'),
    path('404/', views.page_404, name='page_404'),
]