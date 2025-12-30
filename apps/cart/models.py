"""
مدل‌های اپ cart
سبد خرید و کد تخفیف
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class Coupon(models.Model):
    """کد تخفیف"""
    
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'درصدی'),
        ('fixed', 'مبلغ ثابت'),
    ]
    
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='کد تخفیف'
    )
    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percent',
        verbose_name='نوع تخفیف'
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        verbose_name='مقدار تخفیف'
    )
    min_purchase = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name='حداقل مبلغ خرید'
    )
    max_discount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name='حداکثر تخفیف',
        help_text='فقط برای تخفیف درصدی'
    )
    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='محدودیت استفاده کلی'
    )
    usage_limit_per_user = models.PositiveIntegerField(
        default=1,
        verbose_name='محدودیت استفاده هر کاربر'
    )
    used_count = models.PositiveIntegerField(
        default=0,
        verbose_name='تعداد استفاده'
    )
    
    valid_from = models.DateTimeField(verbose_name='معتبر از')
    valid_until = models.DateTimeField(verbose_name='معتبر تا')
    
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = 'کد تخفیف'
        verbose_name_plural = 'کدهای تخفیف'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.code
    
    def is_valid(self, user=None, total=0):
        """بررسی اعتبار کد تخفیف"""
        now = timezone.now()
        
        if not self.is_active:
            return False, 'کد تخفیف غیرفعال است'
        
        if now < self.valid_from:
            return False, 'کد تخفیف هنوز فعال نشده است'
        
        if now > self.valid_until:
            return False, 'کد تخفیف منقضی شده است'
        
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False, 'ظرفیت استفاده از این کد تخفیف تمام شده است'
        
        if total < self.min_purchase:
            return False, f'حداقل مبلغ خرید {self.min_purchase:,} تومان است'
        
        if user and user.is_authenticated:
            user_usage = CouponUsage.objects.filter(
                coupon=self,
                user=user
            ).count()
            if user_usage >= self.usage_limit_per_user:
                return False, 'شما قبلاً از این کد تخفیف استفاده کرده‌اید'
        
        return True, 'کد تخفیف معتبر است'
    
    def calculate_discount(self, total):
        """محاسبه مقدار تخفیف"""
        if self.discount_type == 'percent':
            discount = total * self.discount_value / 100
            if self.max_discount:
                discount = min(discount, self.max_discount)
        else:
            discount = self.discount_value
        
        return min(discount, total)


class CouponUsage(models.Model):
    """سابقه استفاده از کد تخفیف"""
    
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name='usages',
        verbose_name='کد تخفیف'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coupon_usages',
        verbose_name='کاربر'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coupon_usage',
        verbose_name='سفارش'
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='مبلغ تخفیف'
    )
    used_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ استفاده')
    
    class Meta:
        verbose_name = 'استفاده از کد تخفیف'
        verbose_name_plural = 'سوابق استفاده از کدهای تخفیف'
        ordering = ['-used_at']
    
    def __str__(self):
        return f'{self.user.phone} - {self.coupon.code}'


class Cart(models.Model):
    """سبد خرید"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts',
        verbose_name='کاربر'
    )
    session_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='کلید نشست'
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='carts',
        verbose_name='کد تخفیف'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبدهای خرید'
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.user:
            return f'سبد {self.user.phone}'
        return f'سبد مهمان {self.session_key[:8]}'
    
    @property
    def subtotal(self):
        """جمع کل بدون تخفیف"""
        return sum(item.total_price for item in self.items.all())
    
    @property
    def discount_amount(self):
        """مبلغ تخفیف"""
        if self.coupon:
            is_valid, _ = self.coupon.is_valid(self.user, self.subtotal)
            if is_valid:
                return self.coupon.calculate_discount(self.subtotal)
        return Decimal('0')
    
    @property
    def total(self):
        """جمع کل با تخفیف"""
        return self.subtotal - self.discount_amount
    
    @property
    def items_count(self):
        """تعداد آیتم‌ها"""
        return sum(item.quantity for item in self.items.all())
    
    def add_item(self, product, quantity=1):
        """افزودن آیتم به سبد"""
        item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            defaults={
                'quantity': quantity,
                'price_snapshot': product.price
            }
        )
        
        if not created:
            # بروزرسانی تعداد
            new_quantity = item.quantity + quantity
            
            # بررسی حداکثر تعداد مجاز
            max_qty = min(product.stock_quantity, product.max_purchase_per_user)
            if new_quantity > max_qty:
                new_quantity = max_qty
            
            item.quantity = new_quantity
            item.save()
        
        return item
    
    def remove_item(self, product):
        """حذف آیتم از سبد"""
        CartItem.objects.filter(cart=self, product=product).delete()
    
    def update_item_quantity(self, product, quantity):
        """بروزرسانی تعداد آیتم"""
        try:
            item = self.items.get(product=product)
            if quantity <= 0:
                item.delete()
            else:
                # بررسی حداکثر تعداد مجاز
                max_qty = min(product.stock_quantity, product.max_purchase_per_user)
                item.quantity = min(quantity, max_qty)
                item.save()
        except CartItem.DoesNotExist:
            pass
    
    def clear(self):
        """خالی کردن سبد"""
        self.items.all().delete()
        self.coupon = None
        self.save()
    
    def apply_coupon(self, code, user=None):
        """اعمال کد تخفیف"""
        try:
            coupon = Coupon.objects.get(code=code)
            is_valid, message = coupon.is_valid(user, self.subtotal)
            
            if is_valid:
                self.coupon = coupon
                self.save()
                return True, message
            return False, message
        except Coupon.DoesNotExist:
            return False, 'کد تخفیف یافت نشد'
    
    def remove_coupon(self):
        """حذف کد تخفیف"""
        self.coupon = None
        self.save()


class CartItem(models.Model):
    """آیتم سبد خرید"""
    
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='سبد'
    )
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='محصول'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='تعداد'
    )
    price_snapshot = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name='قیمت در زمان افزودن'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ افزودن')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = 'آیتم سبد خرید'
        verbose_name_plural = 'آیتم‌های سبد خرید'
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f'{self.product.name} × {self.quantity}'
    
    @property
    def total_price(self):
        """قیمت کل آیتم"""
        return self.product.price * self.quantity
    
    @property
    def is_available(self):
        """بررسی موجودی"""
        return (
            self.product.is_active and
            self.product.is_in_stock and
            self.product.stock_quantity >= self.quantity
        )
