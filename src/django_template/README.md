# قالب Django گل ناز (Golnaz Shop Django Template)

## توضیحات

این پروژه، تبدیل کامل قالب HTML گل ناز به یک قالب Django است که با معماری MVT و template system Django کاملاً سازگار می‌باشد.

## ویژگی‌های پروژه

### ✅ **ویژگی‌های اصلی:**
- **Template Inheritance**: استفاده از base template برای inheritance
- **Static Files Management**: مدیریت فایل‌های static (CSS, JS, Images, Fonts)
- **Responsive Design**: حفظ کامل responsive design اصلی
- **Django Template Tags**: استفاده از Django template tags و filters
- **MVT Architecture**: پیاده‌سازی کامل معماری Model-View-Template

### 🎨 **ویژگی‌های UI/UX:**
- طراحی کاملاً فارسی و RTL
- Alpine.js برای تعاملات JavaScript
- Swiper.js برای اسلایدرها
- TailwindCSS برای استایل‌دهی
- فونت‌های فارسی (IRANYekanX، دانا، یکان‌باخ)

## ساختار پروژه

```
django_template/
├── golnaz_project/          # Django project
│   ├── __init__.py
│   ├── settings.py         # تنظیمات Django
│   ├── urls.py             # URL patterns اصلی
│   └── wsgi.py
├── shop/                   # Django app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py            # URL patterns app
│   ├── views.py           # View functions
│   └── ...
├── templates/              # Django templates
│   ├── base.html          # Base template
│   ├── home.html          # صفحه اصلی
│   ├── shop.html          # فروشگاه
│   └── includes/          # Template includes
│       ├── header.html    # هدر
│       └── footer.html    # فوتر
├── static/                 # Static files
│   ├── css/               # فایل‌های CSS
│   ├── js/                # فایل‌های JavaScript
│   ├── images/            # تصاویر
│   └── fonts/             # فونت‌ها
└── manage.py              # Django management script
```

## نصب و راه‌اندازی

### پیش‌نیازها:
- Python 3.8+
- Django 6.0+

### مراحل نصب:

1. **کلون کردن پروژه:**
```bash
# پروژه را در مسیر دلخواه کپی کنید
```

2. **ایجاد محیط مجازی:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# یا
venv\Scripts\activate     # Windows
```

3. **نصب وابستگی‌ها:**
```bash
pip install django
```

4. **اجرای migrations:**
```bash
python manage.py migrate
```

5. **اجرای سرور توسعه:**
```bash
python manage.py runserver
```

6. **مشاهده سایت:**
مرورگر خود را باز کرده و به آدرس `http://127.0.0.1:8000` بروید.

## صفحات موجود

### 🏠 **صفحات اصلی:**
- `/ ` - صفحه اصلی (home.html)
- `/shop/` - فروشگاه (shop.html)
- `/product/` - جزئیات محصول (product.html)
- `/about-us/` - درباره ما (about-us.html)
- `/contact-us/` - تماس با ما (contact-us.html)

### 📝 **وبلاگ:**
- `/blog/` - لیست مقالات (blog.html)
- `/blog/<int:blog_id>/` - جزئیات مقاله (blog-single.html)

### 👤 **حساب کاربری:**
- `/account/info/` - اطلاعات حساب (account-info.html)
- `/account/orders/` - سفارشات (orders.html)
- `/account/wishlist/` - علاقه‌مندی‌ها (wishlist.html)
- `/account/addresses/` - آدرس‌ها (addresses.html)
- `/account/messages/` - پیام‌ها (messages.html)
- `/account/reviews/` - نظرات (reviews.html)
- `/account/dashboard/` - داشبورد (dashboard.html)

### 🛒 **خرید:**
- `/cart/` - سبد خرید (shoping-cart.html)
- `/cart/empty/` - سبد خرید خالی (empty-shopping-cart.html)
- `/checkout/shipping/` - اطلاعات ارسال (checkout-shipping.html)
- `/checkout/payment/` - پرداخت (checkout-payment.html)
- `/payment/success/` - پرداخت موفق (success_payment.html)
- `/payment/failed/` - پرداخت ناموفق (payment_failed.html)

### 🔐 **احراز هویت:**
- `/login/` - ورود (login.html)
- `/login/otp/` - ورود با OTP (login-otp.html)

### 🛠 **صفحات خاص:**
- `/maintenance/` - تعمیرات (maintenance.html)
- `/404/` - صفحه 404 (404.html)

## نکات مهم

### 📱 **Responsive Design:**
- طراحی کاملاً responsive حفظ شده
- Mobile-first approach
- Breakpoints مطابق با TailwindCSS

### 🎨 **استایل‌دهی:**
- استفاده از TailwindCSS classes
- CSS سفارشی در `static/css/main.css`
- فونت‌های فارسی بهینه

### ⚡ **JavaScript:**
- Alpine.js برای تعاملات
- Swiper.js برای اسلایدرها
- Bundle شده در `static/js/bundle26.js`

### 🔧 **قابلیت‌های Django:**
- Template inheritance با `{% extends %}`
- Static files با `{% static %}`
- URL patterns با `{% url %}`
- Template tags و filters

## توسعه بیشتر

### اضافه کردن صفحه جدید:

1. **View function در `shop/views.py`:**
```python
def new_page(request):
    return render(request, 'new_page.html')
```

2. **URL pattern در `shop/urls.py`:**
```python
path('new-page/', views.new_page, name='new_page'),
```

3. **Template در `templates/new_page.html`:**
```html
{% extends 'base.html' %}
{% block content %}
<!-- محتوای صفحه -->
{% endblock %}
```

### تنظیمات Production:

1. `DEBUG = False` در settings.py
2. تنظیم `ALLOWED_HOSTS`
3. تنظیم static files برای production
4. استفاده از database production

## لایسنس

این پروژه تحت لایسنس MIT منتشر شده است.

---

**نکته:** این قالب کاملاً آماده استفاده و قابل توسعه برای پروژه‌های فروشگاهی با Django است.