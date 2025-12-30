"""
سیگنال‌های مربوط به سفارشات
"""
import logging
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(pre_save, sender='orders.Order')
def order_status_changing(sender, instance, **kwargs):
    """
    ذخیره وضعیت قبلی سفارش قبل از تغییر
    """
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
            instance._old_status_display = old_instance.get_status_display()
        except sender.DoesNotExist:
            instance._old_status = None
            instance._old_status_display = None
    else:
        instance._old_status = None
        instance._old_status_display = None


@receiver(post_save, sender='orders.Order')
def order_status_changed(sender, instance, created, **kwargs):
    """
    ارسال پیامک هنگام تغییر وضعیت سفارش
    """
    # اگر سفارش جدید است، پیامکی ارسال نمی‌شود
    if created:
        return
    
    old_status = getattr(instance, '_old_status', None)
    
    # اگر وضعیت تغییر نکرده، پیامکی ارسال نمی‌شود
    if old_status is None or old_status == instance.status:
        return
    
    old_status_display = getattr(instance, '_old_status_display', old_status)
    new_status_display = instance.get_status_display()
    
    # دریافت نام محصولات سفارش
    product_names = []
    for item in instance.items.all():
        if item.product:
            product_names.append(item.product.name)
    
    product_name = '، '.join(product_names[:3])  # حداکثر 3 محصول نمایش داده شود
    if len(product_names) > 3:
        product_name += f' و {len(product_names) - 3} محصول دیگر'
    
    if not product_name:
        product_name = f'سفارش {instance.order_number}'
    
    # دریافت اطلاعات کاربر
    customer_name = instance.user.get_full_name() or instance.user.phone
    phone = instance.receiver_phone or instance.user.phone
    
    if not phone:
        logger.warning(f"شماره تلفن برای سفارش {instance.order_number} یافت نشد")
        return
    
    logger.info(
        f"تغییر وضعیت سفارش {instance.order_number}: "
        f"{old_status_display} -> {new_status_display}"
    )
    
    # ارسال پیامک
    try:
        from apps.core.sms import send_order_status_sms
        
        result = send_order_status_sms(
            phone=phone,
            customer_name=customer_name,
            product_name=product_name,
            old_status=old_status_display,
            new_status=new_status_display
        )
        
        if result['success']:
            logger.info(f"پیامک تغییر وضعیت به {phone} ارسال شد")
        else:
            logger.warning(f"خطا در ارسال پیامک تغییر وضعیت: {result['message']}")
            
    except Exception as e:
        logger.error(f"خطا در ارسال پیامک تغییر وضعیت: {e}")
