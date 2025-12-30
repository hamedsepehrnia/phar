# راه‌حل مشکل Active Menu Navigation

## مشکل
در نسخه دسکتاپ، منوی navigation فقط برای صفحه اصلی (Home) active state (رنگ بنفش) را نشان می‌داد و سایر منوها هنگام بازدید active نمی‌شدند.

## تحلیل مشکل
1. **CSS**: کلاس `.menu-item_link.active::after` و `.menu-item_link:hover::after` در CSS تعریف شده بود
2. **Template**: کلاس `active` به menu item های مناسب اضافه نمی‌شد
3. **Logic**: منطق تشخیص active menu item بر اساس URL فعلی وجود نداشت

## راه‌حل پیاده‌سازی شده

### 1. اصلاح Header Template
فایل: `templates/partials/header.html`

هر menu item حالا شامل این منطق است:
```html
<a href="{% url 'core:home' %}" class="menu-item_link relative inline-flex items-center gap-x-2 {% if request.resolver_match.url_name == 'home' and request.resolver_match.namespace == 'core' %}active{% endif %}">
```

### 2. منطق تشخیص Active State

#### صفحه اصلی (Home)
```django
{% if request.resolver_match.url_name == 'home' and request.resolver_match.namespace == 'core' %}active{% endif %}
```

#### بخش کاتالوگ (محصولات)  
```django
{% if request.resolver_match.namespace == 'catalog' %}active{% endif %}
```

#### جدیدترین محصولات
```django
{% if request.GET.sort == 'newest' or request.resolver_match.namespace == 'catalog' and request.resolver_match.url_name == 'shop' and not request.GET.sort %}active{% endif %}
```

#### پرفروش‌ترین محصولات
```django
{% if request.GET.sort == 'popular' %}active{% endif %}
```

#### درباره ما
```django
{% if request.resolver_match.url_name == 'about' and request.resolver_match.namespace == 'core' %}active{% endif %}
```

#### تماس با ما
```django
{% if request.resolver_match.url_name == 'contact' and request.resolver_match.namespace == 'core' %}active{% endif %}
```

### 3. رنگ‌بندی آیکون و متن
برای هر menu item، رنگ آیکون و متن بر اساس active state تنظیم می‌شود:
```django
class="{% if condition %}text-primary-800{% else %}text-gray-600{% endif %}"
```

## ویژگی‌های اضافه شده

### 1. تشخیص هوشمند Active State
- **صفحه اصلی**: فقط روی home page
- **کاتالوگ**: روی تمام صفحات مربوط به محصولات (shop, product_detail, category_detail, etc.)
- **جدیدترین**: روی shop page بدون filter یا با `sort=newest`
- **پرفروش‌ترین**: روی shop page با `sort=popular`
- **صفحات استاتیک**: بر اساس URL name دقیق

### 2. استایل Visual
- **Active State**: رنگ بنفش (`text-primary-800`) + خط زیر menu item
- **Inactive State**: رنگ خاکستری (`text-gray-600`)
- **Hover Effect**: انیمیشن خط زیر menu item

### 3. پشتیبانی کامل از URL Structure
راه‌حل با ساختار URL های مختلف کار می‌کند:
- `/` - صفحه اصلی
- `/catalog/` - لیست محصولات
- `/catalog/product/slug/` - جزئیات محصول  
- `/catalog/?sort=newest` - جدیدترین محصولات
- `/catalog/?sort=popular` - پرفروش‌ترین محصولات
- `/about/` - درباره ما
- `/contact/` - تماس با ما

## تست

برای تست، بازدید کنید از:
1. صفحه اصلی - منوی "صفحه اصلی" باید active باشد
2. `/catalog/` - منوی "دسته بندی محصولات" باید active باشد
3. `/catalog/?sort=newest` - منوی "جدیدترین ها" باید active باشد
4. `/catalog/?sort=popular` - منوی "پرفروش‌ترین ها" باید active باشد
5. `/about/` - منوی "درباره ما" باید active باشد
6. `/contact/` - منوی "تماس با ما" باید active باشد

## نکات مهم

1. **Namespace**: همیشه namespace را در شرط‌ها بررسی کنید
2. **URL Parameters**: برای menu های با query parameter (مثل sort) پارامترها را چک کنید
3. **Default State**: برای "جدیدترین" که default sort است، شرط خاص نیاز دارد
4. **CSS**: کلاس `active` باعث نمایش خط زیر menu item می‌شود

## فایل‌های تغییر یافته
- `templates/partials/header.html` - منطق active state اضافه شد
- CSS های موجود در `static/css/main.css` - بدون تغییر، قبلاً آماده بود