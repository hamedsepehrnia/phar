from django.shortcuts import render

def home(request):
    """صفحه اصلی"""
    return render(request, 'home.html')

def shop(request):
    """صفحه فروشگاه"""
    return render(request, 'shop.html')

def product_detail(request, product_id=None):
    """جزئیات محصول"""
    return render(request, 'product.html')

def about_us(request):
    """درباره ما"""
    return render(request, 'about-us.html')

def contact_us(request):
    """تماس با ما"""
    return render(request, 'contact-us.html')

def blog(request):
    """وبلاگ"""
    return render(request, 'blog.html')

def blog_single(request, blog_id=None):
    """جزئیات مقاله وبلاگ"""
    return render(request, 'blog-single.html')

def account_info(request):
    """اطلاعات حساب کاربری"""
    return render(request, 'account-info.html')

def orders(request):
    """سفارشات کاربر"""
    return render(request, 'orders.html')

def wishlist(request):
    """علاقه‌مندی‌ها"""
    return render(request, 'wishlist.html')

def addresses(request):
    """آدرس‌های کاربر"""
    return render(request, 'addresses.html')

def messages(request):
    """پیام‌های کاربر"""
    return render(request, 'messages.html')

def reviews(request):
    """نظرات کاربر"""
    return render(request, 'reviews.html')

def dashboard(request):
    """داشبورد کاربر"""
    return render(request, 'dashboard.html')

def shopping_cart(request):
    """سبد خرید"""
    return render(request, 'shoping-cart.html')

def empty_cart(request):
    """سبد خرید خالی"""
    return render(request, 'empty-shopping-cart.html')

def checkout_shipping(request):
    """تسویه حساب - اطلاعات ارسال"""
    return render(request, 'checkout-shipping.html')

def checkout_payment(request):
    """تسویه حساب - پرداخت"""
    return render(request, 'checkout-payment.html')

def payment_success(request):
    """پرداخت موفق"""
    return render(request, 'success_payment.html')

def payment_failed(request):
    """پرداخت ناموفق"""
    return render(request, 'payment_failed.html')

def login_view(request):
    """ورود"""
    return render(request, 'login.html')

def login_otp(request):
    """ورود با OTP"""
    return render(request, 'login-otp.html')

def maintenance(request):
    """صفحه تعمیرات"""
    return render(request, 'maintenance.html')

def page_404(request):
    """صفحه 404"""
    return render(request, '404.html')

def home(request):
    """صفحه اصلی"""
    return render(request, 'shop/index.html')

def shop(request):
    """صفحه فروشگاه"""
    return render(request, 'shop/shop.html')

def product_detail(request, product_id):
    """جزئیات محصول"""
    context = {'product_id': product_id}
    return render(request, 'shop/product.html', context)

def blog(request):
    """صفحه وبلاگ"""
    return render(request, 'shop/blog.html')

def blog_single(request, post_id):
    """جزئیات پست وبلاگ"""
    context = {'post_id': post_id}
    return render(request, 'shop/blog-single.html', context)

def about_us(request):
    """درباره ما"""
    return render(request, 'shop/about-us.html')

def contact_us(request):
    """تماس با ما"""
    return render(request, 'shop/contact-us.html')

def login(request):
    """ورود"""
    return render(request, 'shop/login.html')

def login_otp(request):
    """ورود با OTP"""
    return render(request, 'shop/login-otp.html')

def dashboard(request):
    """داشبورد کاربر"""
    return render(request, 'shop/dashboard.html')

def account_info(request):
    """اطلاعات حساب کاربری"""
    return render(request, 'shop/account-info.html')

def orders(request):
    """سفارشات"""
    return render(request, 'shop/orders.html')

def addresses(request):
    """آدرس‌ها"""
    return render(request, 'shop/addresses.html')

def wishlist(request):
    """لیست علاقه‌مندی‌ها"""
    return render(request, 'shop/wishlist.html')

def shopping_cart(request):
    """سبد خرید"""
    return render(request, 'shop/shopping-cart.html')

def empty_shopping_cart(request):
    """سبد خرید خالی"""
    return render(request, 'shop/empty-shopping-cart.html')

def checkout_shipping(request):
    """تسویه حساب - ارسال"""
    return render(request, 'shop/checkout-shipping.html')

def checkout_payment(request):
    """تسویه حساب - پرداخت"""
    return render(request, 'shop/checkout-payment.html')

def success_payment(request):
    """پرداخت موفق"""
    return render(request, 'shop/success-payment.html')

def payment_failed(request):
    """پرداخت ناموفق"""
    return render(request, 'shop/payment-failed.html')

def messages(request):
    """پیام‌ها"""
    return render(request, 'shop/messages.html')

def reviews(request):
    """نظرات"""
    return render(request, 'shop/reviews.html')

def maintenance(request):
    """در حال تعمیر"""
    return render(request, 'shop/maintenance.html')

def page_404(request):
    """صفحه 404"""
    return render(request, 'shop/404.html')
