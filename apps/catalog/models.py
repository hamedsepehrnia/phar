"""
مدل‌های اپ catalog
دسته‌بندی درختی با MPTT، محصولات، برند، ویژگی‌ها
"""
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.text import slugify


class Category(MPTTModel):
    """دسته‌بندی درختی محصولات"""
    
    name = models.CharField(max_length=100, verbose_name='نام دسته')
    slug = models.SlugField(
        max_length=100,
        unique=True,
        allow_unicode=True,
        verbose_name='نامک'
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='دسته والد'
    )
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        verbose_name='تصویر'
    )
    description = models.TextField(blank=True, verbose_name='توضیحات')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    
    # SEO fields
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
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class MPTTMeta:
        order_insertion_by = ['sort_order', 'name']
    
    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('catalog:category_detail', kwargs={'slug': self.slug})
    
    def get_active_products(self):
        """محصولات فعال این دسته و زیردسته‌ها"""
        descendants = self.get_descendants(include_self=True)
        return Product.objects.filter(
            category__in=descendants,
            is_active=True
        )


class Brand(models.Model):
    """برند محصولات"""
    
    name = models.CharField(max_length=100, verbose_name='نام برند')
    slug = models.SlugField(
        max_length=100,
        unique=True,
        allow_unicode=True,
        verbose_name='نامک'
    )
    logo = models.ImageField(
        upload_to='brands/',
        blank=True,
        null=True,
        verbose_name='لوگو'
    )
    description = models.TextField(blank=True, verbose_name='توضیحات')
    country = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='کشور سازنده'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برندها'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('catalog:brand_detail', kwargs={'slug': self.slug})


class ProductAttribute(models.Model):
    """ویژگی‌های محصول (حجم، دوز، شکل دارویی و ...)"""
    
    name = models.CharField(max_length=100, verbose_name='نام ویژگی')
    
    class Meta:
        verbose_name = 'ویژگی محصول'
        verbose_name_plural = 'ویژگی‌های محصول'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """محصول"""
    
    name = models.CharField(max_length=255, verbose_name='نام محصول')
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        verbose_name='نامک'
    )
    description = models.TextField(blank=True, verbose_name='توضیحات')
    short_description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='توضیح کوتاه'
    )
    
    category = TreeForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='دسته‌بندی'
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='برند'
    )
    
    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        verbose_name='قیمت (تومان)'
    )
    compare_at_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name='قیمت قبل از تخفیف'
    )
    
    sku = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='کد کالا (SKU)'
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='موجودی'
    )
    is_in_stock = models.BooleanField(default=True, verbose_name='موجود')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    # فیلدهای مخصوص دارو
    prescription_required = models.BooleanField(
        default=False,
        verbose_name='نیاز به نسخه'
    )
    expiry_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاریخ انقضا'
    )
    batch_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='شماره بچ'
    )
    max_purchase_per_user = models.PositiveSmallIntegerField(
        default=10,
        verbose_name='حداکثر خرید هر کاربر'
    )
    
    # SEO fields
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
    
    # Statistics
    view_count = models.PositiveIntegerField(
        default=0,
        verbose_name='تعداد بازدید'
    )
    sales_count = models.PositiveIntegerField(
        default=0,
        verbose_name='تعداد فروش'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['is_active', 'is_in_stock']),
            models.Index(fields=['price']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        
        # بروزرسانی وضعیت موجودی
        self.is_in_stock = self.stock_quantity > 0
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={'slug': self.slug})
    
    @property
    def main_image(self):
        """تصویر اصلی محصول"""
        image = self.images.filter(is_main=True).first()
        if not image:
            image = self.images.first()
        return image
    
    @property
    def discount_percent(self):
        """درصد تخفیف"""
        if self.compare_at_price and self.compare_at_price > self.price:
            discount = (self.compare_at_price - self.price) / self.compare_at_price * 100
            return int(discount)
        return 0
    
    def get_related_products(self, limit=4):
        """محصولات مرتبط"""
        return Product.objects.filter(
            category=self.category,
            is_active=True
        ).exclude(pk=self.pk)[:limit]


class ProductImage(models.Model):
    """تصاویر محصول"""
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='محصول'
    )
    image = models.ImageField(
        upload_to='products/',
        verbose_name='تصویر'
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='متن جایگزین'
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name='تصویر اصلی'
    )
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='ترتیب'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'تصاویر محصول'
        ordering = ['sort_order', '-is_main']
    
    def __str__(self):
        return f'{self.product.name} - تصویر {self.pk}'
    
    def save(self, *args, **kwargs):
        if self.is_main:
            # فقط یک تصویر می‌تواند اصلی باشد
            ProductImage.objects.filter(
                product=self.product,
                is_main=True
            ).exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)


class ProductAttributeValue(models.Model):
    """مقادیر ویژگی‌های محصول"""
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='attribute_values',
        verbose_name='محصول'
    )
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name='ویژگی'
    )
    value = models.CharField(max_length=255, verbose_name='مقدار')
    
    class Meta:
        verbose_name = 'مقدار ویژگی'
        verbose_name_plural = 'مقادیر ویژگی‌ها'
        unique_together = ['product', 'attribute']
    
    def __str__(self):
        return f'{self.product.name} - {self.attribute.name}: {self.value}'


class Wishlist(models.Model):
    """لیست علاقه‌مندی‌ها"""
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='wishlists',
        verbose_name='کاربر'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='wishlisted_by',
        verbose_name='محصول'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ افزودن')
    
    class Meta:
        verbose_name = 'علاقه‌مندی'
        verbose_name_plural = 'علاقه‌مندی‌ها'
        unique_together = ['user', 'product']
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.phone} - {self.product.name}'
