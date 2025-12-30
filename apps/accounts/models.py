"""
مدل‌های اپ accounts
Custom User Model و مدل‌های مرتبط با کاربر
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone
import random
import string


class UserManager(BaseUserManager):
    """مدیریت ایجاد کاربران"""
    
    def create_user(self, phone, password=None, **extra_fields):
        """ایجاد کاربر عادی"""
        if not phone:
            raise ValueError('شماره موبایل الزامی است')
        
        user = self.model(phone=phone, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, password=None, **extra_fields):
        """ایجاد ادمین"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """مدل کاربر سفارشی با شماره موبایل به عنوان شناسه"""
    
    GENDER_CHOICES = [
        ('M', 'مرد'),
        ('F', 'زن'),
    ]
    
    phone_validator = RegexValidator(
        regex=r'^09\d{9}$',
        message='شماره موبایل باید با 09 شروع شود و 11 رقم باشد'
    )
    
    national_code_validator = RegexValidator(
        regex=r'^\d{10}$',
        message='کد ملی باید 10 رقم باشد'
    )
    
    phone = models.CharField(
        max_length=11,
        unique=True,
        validators=[phone_validator],
        verbose_name='شماره موبایل'
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='ایمیل'
    )
    first_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='نام'
    )
    last_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='نام خانوادگی'
    )
    national_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        unique=True,
        validators=[national_code_validator],
        verbose_name='کد ملی'
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        verbose_name='جنسیت'
    )
    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاریخ تولد'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='تصویر پروفایل'
    )
    
    is_staff = models.BooleanField(default=False, verbose_name='دسترسی ادمین')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    is_verified = models.BooleanField(default=False, verbose_name='تایید شده')
    
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='تاریخ عضویت')
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='آخرین ورود')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.get_full_name() or self.phone
    
    def get_full_name(self):
        """نام کامل کاربر"""
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.phone
    
    def get_short_name(self):
        """نام کوتاه کاربر"""
        return self.first_name or self.phone


class OTPCode(models.Model):
    """مدل کد یکبار مصرف"""
    
    phone = models.CharField(max_length=11, verbose_name='شماره موبایل')
    code = models.CharField(max_length=6, verbose_name='کد')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    is_used = models.BooleanField(default=False, verbose_name='استفاده شده')
    attempts = models.PositiveSmallIntegerField(default=0, verbose_name='تعداد تلاش')
    
    class Meta:
        verbose_name = 'کد یکبار مصرف'
        verbose_name_plural = 'کدهای یکبار مصرف'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.phone} - {self.code}'
    
    @classmethod
    def generate_code(cls):
        """تولید کد 6 رقمی تصادفی"""
        return ''.join(random.choices(string.digits, k=6))
    
    def is_valid(self):
        """بررسی اعتبار کد"""
        from django.conf import settings
        from datetime import timedelta
        
        expiry_minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 3)
        expiry_time = self.created_at + timedelta(minutes=expiry_minutes)
        
        return (
            not self.is_used and
            timezone.now() < expiry_time and
            self.attempts < 3
        )


class Address(models.Model):
    """مدل آدرس کاربر"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='addresses',
        verbose_name='کاربر'
    )
    title = models.CharField(
        max_length=50,
        verbose_name='عنوان آدرس',
        help_text='مثال: منزل، محل کار'
    )
    province = models.CharField(max_length=50, verbose_name='استان')
    city = models.CharField(max_length=50, verbose_name='شهر')
    address = models.TextField(verbose_name='آدرس کامل')
    postal_code = models.CharField(
        max_length=10,
        verbose_name='کد پستی'
    )
    receiver_name = models.CharField(
        max_length=100,
        verbose_name='نام گیرنده'
    )
    receiver_phone = models.CharField(
        max_length=11,
        verbose_name='شماره تماس گیرنده'
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='آدرس پیش‌فرض'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    
    class Meta:
        verbose_name = 'آدرس'
        verbose_name_plural = 'آدرس‌ها'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f'{self.title} - {self.user.phone}'
    
    def save(self, *args, **kwargs):
        """اگر آدرس پیش‌فرض است، بقیه را غیرپیش‌فرض کن"""
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
    
    def get_full_address(self):
        """آدرس کامل"""
        return f'{self.province}، {self.city}، {self.address}'
