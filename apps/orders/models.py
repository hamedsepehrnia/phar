"""
مدل‌های اپ orders
سفارش، آیتم سفارش، پرداخت
"""
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import uuid


class Order(models.Model):
    """سفارش"""
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('processing', 'در حال پردازش'),
        ('shipped', 'ارسال شده'),
        ('delivered', 'تحویل داده شده'),
        ('canceled', 'لغو شده'),
        ('returned', 'مرجوع شده'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='کاربر'
    )
    order_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name='شماره سفارش'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    
    # اطلاعات آدرس (کپی از آدرس انتخابی)
    address_title = models.CharField(max_length=50, verbose_name='عنوان آدرس')
    address_province = models.CharField(max_length=50, verbose_name='استان')
    address_city = models.CharField(max_length=50, verbose_name='شهر')
    address_full = models.TextField(verbose_name='آدرس کامل')
    address_postal_code = models.CharField(max_length=10, verbose_name='کد پستی')
    receiver_name = models.CharField(max_length=100, verbose_name='نام گیرنده')
    receiver_phone = models.CharField(max_length=11, verbose_name='تلفن گیرنده')
    
    # مبالغ
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='جمع کل'
    )
    shipping_cost = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        verbose_name='هزینه ارسال'
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='مبلغ تخفیف'
    )
    coupon_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='کد تخفیف استفاده شده'
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='مبلغ نهایی'
    )
    
    # یادداشت
    note = models.TextField(blank=True, verbose_name='یادداشت مشتری')
    admin_note = models.TextField(blank=True, verbose_name='یادداشت ادمین')
    
    # ارسال
    shipping_method = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='روش ارسال'
    )
    tracking_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='کد رهگیری'
    )
    
    # تاریخ‌ها
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ پرداخت')
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ ارسال')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ تحویل')
    
    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارشات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'سفارش {self.order_number}'
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_order_number():
        """تولید شماره سفارش یکتا"""
        from datetime import datetime
        prefix = datetime.now().strftime('%Y%m%d')
        suffix = uuid.uuid4().hex[:6].upper()
        return f'{prefix}-{suffix}'
    
    def get_absolute_url(self):
        return reverse('dashboard:order_detail', kwargs={'pk': self.pk})
    
    @property
    def status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    
    @property
    def can_cancel(self):
        """آیا امکان لغو سفارش وجود دارد؟"""
        return self.status in ['pending', 'paid']
    
    @property
    def can_pay(self):
        """آیا امکان پرداخت سفارش وجود دارد؟ (تا ۲ ساعت بعد از ایجاد)"""
        if self.status != 'pending':
            return False
        # فقط تا ۲ ساعت بعد از ایجاد سفارش
        from datetime import timedelta
        expiry_time = self.created_at + timedelta(hours=2)
        return timezone.now() < expiry_time
    
    @property
    def payment_time_remaining(self):
        """زمان باقی‌مانده برای پرداخت (به ثانیه)"""
        if self.status != 'pending':
            return 0
        from datetime import timedelta
        expiry_time = self.created_at + timedelta(hours=2)
        remaining = expiry_time - timezone.now()
        return max(0, int(remaining.total_seconds()))
    
    @property
    def payment_expiry_time(self):
        """زمان انقضای پرداخت"""
        from datetime import timedelta
        return self.created_at + timedelta(hours=2)
    
    def cancel(self):
        """لغو سفارش و برگرداندن موجودی"""
        if not self.can_cancel:
            return False
        
        # برگرداندن موجودی
        for item in self.items.all():
            item.product.stock_quantity += item.quantity
            item.product.save()
        
        self.status = 'canceled'
        self.save()
        return True


class OrderItem(models.Model):
    """آیتم سفارش"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='سفارش'
    )
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name='محصول'
    )
    quantity = models.PositiveIntegerField(verbose_name='تعداد')
    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='قیمت واحد'
    )
    
    # کپی اطلاعات محصول
    product_name = models.CharField(max_length=255, verbose_name='نام محصول')
    product_sku = models.CharField(max_length=50, verbose_name='کد محصول')
    
    class Meta:
        verbose_name = 'آیتم سفارش'
        verbose_name_plural = 'آیتم‌های سفارش'
    
    def __str__(self):
        return f'{self.product_name or ""} × {self.quantity or 0}'
    
    @property
    def total_price(self):
        if self.price is None or self.quantity is None:
            return 0
        return self.price * self.quantity
    
    def save(self, *args, **kwargs):
        # کپی اطلاعات محصول
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_sku:
            self.product_sku = self.product.sku
        super().save(*args, **kwargs)


class PaymentTransaction(models.Model):
    """تراکنش پرداخت"""
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('success', 'موفق'),
        ('failed', 'ناموفق'),
        ('canceled', 'لغو شده'),
    ]
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='سفارش'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='مبلغ'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    
    # اطلاعات درگاه
    gateway = models.CharField(
        max_length=50,
        default='zarinpal',
        verbose_name='درگاه پرداخت'
    )
    authority = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='کد مرجع درگاه'
    )
    ref_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='شماره پیگیری'
    )
    card_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='شماره کارت'
    )
    
    # تاریخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = 'تراکنش پرداخت'
        verbose_name_plural = 'تراکنش‌های پرداخت'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.order.order_number} - {self.get_status_display()}'


class ShippingMethod(models.Model):
    """روش ارسال"""
    
    name = models.CharField(max_length=100, verbose_name='نام')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='هزینه'
    )
    min_delivery_days = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='حداقل روز ارسال'
    )
    max_delivery_days = models.PositiveSmallIntegerField(
        default=3,
        verbose_name='حداکثر روز ارسال'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب')
    
    class Meta:
        verbose_name = 'روش ارسال'
        verbose_name_plural = 'روش‌های ارسال'
        ordering = ['sort_order', 'price']
    
    def __str__(self):
        return self.name
    
    @property
    def delivery_estimate(self):
        if self.min_delivery_days == self.max_delivery_days:
            return f'{self.min_delivery_days} روز'
        return f'{self.min_delivery_days} تا {self.max_delivery_days} روز'
