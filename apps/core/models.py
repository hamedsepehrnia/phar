"""
مدل‌های اپ core
تنظیمات عمومی، صفحات ایستا
"""
from django.db import models


class SiteSettings(models.Model):
    """تنظیمات سایت"""
    
    site_name = models.CharField(max_length=100, verbose_name='نام سایت')
    site_description = models.TextField(blank=True, verbose_name='توضیحات سایت')
    logo = models.ImageField(
        upload_to='settings/',
        blank=True,
        null=True,
        verbose_name='لوگو'
    )
    favicon = models.ImageField(
        upload_to='settings/',
        blank=True,
        null=True,
        verbose_name='فاوآیکون'
    )
    
    # اطلاعات تماس
    phone = models.CharField(max_length=20, blank=True, verbose_name='تلفن')
    phone_2 = models.CharField(max_length=20, blank=True, verbose_name='تلفن ۲')
    email = models.EmailField(blank=True, verbose_name='ایمیل')
    address = models.TextField(blank=True, verbose_name='آدرس')
    
    # شبکه‌های اجتماعی
    instagram = models.URLField(blank=True, verbose_name='اینستاگرام')
    telegram = models.URLField(blank=True, verbose_name='تلگرام')
    whatsapp = models.CharField(max_length=20, blank=True, verbose_name='واتساپ')

    # نقشه تماس
    map_latitude = models.FloatField(
        default=32.661443,
        verbose_name='عرض جغرافیایی نقشه'
    )
    map_longitude = models.FloatField(
        default=51.666552,
        verbose_name='طول جغرافیایی نقشه'
    )
    map_zoom = models.PositiveSmallIntegerField(
        default=14,
        verbose_name='زوم نقشه'
    )
    
    # متن فوتر
    footer_text = models.TextField(blank=True, verbose_name='متن فوتر')
    copyright_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='متن کپی‌رایت'
    )
    
    # SEO عمومی
    meta_title = models.CharField(
        max_length=70,
        blank=True,
        verbose_name='عنوان متا'
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name='توضیحات متا'
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='کلمات کلیدی'
    )
    
    class Meta:
        verbose_name = 'تنظیمات سایت'
        verbose_name_plural = 'تنظیمات سایت'
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        # فقط یک رکورد تنظیمات باید وجود داشته باشد
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """دریافت تنظیمات"""
        obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={'site_name': 'داروخانه دکتر واعظی'}
        )
        return obj


class Slider(models.Model):
    """اسلایدر صفحه اصلی"""
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    subtitle = models.CharField(max_length=300, blank=True, verbose_name='زیرعنوان')
    image = models.ImageField(upload_to='sliders/', verbose_name='تصویر')
    link = models.URLField(blank=True, verbose_name='لینک')
    button_text = models.CharField(
        max_length=50,
        blank=True,
        default='مشاهده',
        verbose_name='متن دکمه'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'اسلاید'
        verbose_name_plural = 'اسلایدر'
        ordering = ['sort_order', '-created_at']
    
    def __str__(self):
        return self.title


class Banner(models.Model):
    """بنر تبلیغاتی"""
    
    POSITION_CHOICES = [
        ('home_top', 'صفحه اصلی - بالا'),
        ('home_middle', 'صفحه اصلی - وسط'),
        ('home_bottom', 'صفحه اصلی - پایین'),
        ('sidebar', 'سایدبار'),
        ('shop_top', 'فروشگاه - بالا'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    image = models.ImageField(upload_to='banners/', verbose_name='تصویر')
    link = models.URLField(blank=True, verbose_name='لینک')
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        default='home_middle',
        verbose_name='موقعیت'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب')
    
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ شروع'
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ پایان'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'بنر'
        verbose_name_plural = 'بنرها'
        ordering = ['position', 'sort_order']
    
    def __str__(self):
        return self.title


class Page(models.Model):
    """صفحات ایستا"""
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    slug = models.SlugField(
        max_length=200,
        unique=True,
        allow_unicode=True,
        verbose_name='نامک'
    )
    content = models.TextField(verbose_name='محتوا')
    
    meta_title = models.CharField(max_length=70, blank=True, verbose_name='عنوان متا')
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name='توضیحات متا'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    show_in_footer = models.BooleanField(
        default=False,
        verbose_name='نمایش در فوتر'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = 'صفحه'
        verbose_name_plural = 'صفحات'
        ordering = ['title']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('core:page', kwargs={'slug': self.slug})


class ContactMessage(models.Model):
    """پیام‌های تماس"""
    
    name = models.CharField(max_length=100, verbose_name='نام')
    email = models.EmailField(verbose_name='ایمیل')
    phone = models.CharField(max_length=15, blank=True, verbose_name='تلفن')
    subject = models.CharField(max_length=200, verbose_name='موضوع')
    message = models.TextField(verbose_name='پیام')
    
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ')
    
    class Meta:
        verbose_name = 'پیام تماس'
        verbose_name_plural = 'پیام‌های تماس'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} - {self.subject}'


class FAQ(models.Model):
    """سوالات متداول"""
    
    question = models.CharField(max_length=300, verbose_name='سوال')
    answer = models.TextField(verbose_name='پاسخ')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'سوال متداول'
        verbose_name_plural = 'سوالات متداول'
        ordering = ['sort_order']
    
    def __str__(self):
        return self.question[:50]
