# راه‌حل مشکل ۴۰۴ اسلاگ‌های فارسی در پروداکشن

## مشکل
وقتی اسلاگ محصول شامل کاراکترهای فارسی باشد، در محیط پروداکشن خطای ۴۰۴ رخ می‌دهد، در حالی که در محیط توسعه مشکلی وجود ندارد.

## علل احتمالی
1. **URL Encoding**: مرورگر یا وب سرور کاراکترهای فارسی را encode می‌کند
2. **Regex Pattern**: الگوی regex در URL ها کاراکترهای encode شده را شناسایی نمی‌کند
3. **Web Server Config**: تنظیمات nginx/apache برای UTF-8
4. **Database Encoding**: تنظیمات database برای کاراکترهای فارسی

## راه‌حل‌های پیاده‌سازی شده

### 1. تغییر URL Patterns
```python
# قبل: regex محدود
re_path(r'^product/(?P<slug>[-\\w\\u0600-\\u06FF]+)/$', ...)

# بعد: پذیرش همه کاراکترها به جز /
re_path(r'^product/(?P<slug>[^/]+)/$', ...)
```

### 2. اضافه کردن URL Decoding در Views
```python
from urllib.parse import unquote

def get(self, request, slug):
    # URL decode کردن اسلاگ
    decoded_slug = unquote(slug)
    product = get_object_or_404(Product, slug=decoded_slug)
```

### 3. Middleware برای مدیریت Unicode URLs
- `UnicodeURLMiddleware`: مدیریت encoding URLs
- `PersianSlugMiddleware`: redirect اتوماتیک URLs encode شده

### 4. Custom 404 Handler
handler404 هوشمند که:
- URLs encode شده را تشخیص می‌دهد
- سعی می‌کند URL را decode کند و redirect کند
- جستجوی انعطاف‌پذیر در database

## استفاده

### بررسی اسلاگ‌های موجود
```bash
python manage.py check_persian_slugs --verbose
```

### تصحیح اسلاگ‌های مشکل‌دار
```bash
python manage.py check_persian_slugs --fix --verbose
```

## تنظیمات پروداکشن

### Nginx Configuration
```nginx
server {
    charset utf-8;
    
    location / {
        # اطمینان از UTF-8 encoding
        proxy_set_header Accept-Encoding "";
        proxy_pass http://backend;
    }
}
```

### Apache Configuration
```apache
AddDefaultCharset utf-8
```

### Database
اطمینان از UTF-8 collation در database:
```sql
ALTER DATABASE pharmacy_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## نکات مهم

1. **SEO**: استفاده از اسلاگ‌های فارسی برای SEO بهتر است
2. **Backward Compatibility**: کد جدید با URLs قدیمی سازگار است  
3. **Performance**: middleware سبک و بدون تأثیر منفی بر performance
4. **Error Handling**: مدیریت مناسب خطاها و logging

## تست

برای تست در محیط توسعه:
```python
# URL encode کردن دستی اسلاگ فارسی
from urllib.parse import quote
persian_slug = "داروی-ضد-درد"
encoded_slug = quote(persian_slug)
# تست با URL encode شده
```

## Troubleshooting

اگر هنوز مشکل دارید:
1. بررسی logs سرور وب
2. بررسی database encoding
3. تست با curl برای بررسی response headers
4. بررسی Django settings برای UTF-8

```bash
# تست با curl
curl -v "https://yoursite.com/catalog/product/داروی-ضد-درد/"

# بررسی logs
tail -f /var/log/nginx/error.log
```