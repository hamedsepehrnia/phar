"""
مدل‌های اپ reviews
نظرات و امتیازدهی
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    """نظر و امتیاز محصول"""
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار تایید'),
        ('approved', 'تایید شده'),
        ('rejected', 'رد شده'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='کاربر'
    )
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='محصول'
    )
    
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='امتیاز'
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='عنوان'
    )
    content = models.TextField(verbose_name='متن نظر')
    
    # مزایا و معایب
    pros = models.TextField(blank=True, verbose_name='نقاط قوت')
    cons = models.TextField(blank=True, verbose_name='نقاط ضعف')
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    
    is_buyer = models.BooleanField(
        default=False,
        verbose_name='خریدار'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'
        ordering = ['-created_at']
        unique_together = ['user', 'product']
    
    def __str__(self):
        return f'{self.user.get_full_name()} - {self.product.name}'
    
    def save(self, *args, **kwargs):
        # بررسی خریدار بودن
        if not self.pk:
            from apps.orders.models import Order
            self.is_buyer = Order.objects.filter(
                user=self.user,
                items__product=self.product,
                status__in=['paid', 'processing', 'shipped', 'delivered']
            ).exists()
        
        super().save(*args, **kwargs)
