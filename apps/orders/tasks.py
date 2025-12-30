"""
Celery tasks برای سفارشات
"""
import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def cancel_expired_orders():
    """
    لغو سفارش‌های پرداخت نشده بعد از ۲ ساعت
    این تسک هر ۱۵ دقیقه اجرا می‌شود
    """
    from .models import Order
    
    # سفارش‌هایی که بیش از ۲ ساعت از ایجادشان گذشته و هنوز pending هستند
    expiry_time = timezone.now() - timedelta(hours=2)
    
    expired_orders = Order.objects.filter(
        status='pending',
        created_at__lt=expiry_time
    )
    
    canceled_count = 0
    for order in expired_orders:
        order.status = 'canceled'
        order.admin_note = 'لغو خودکار به دلیل عدم پرداخت در زمان مقرر'
        order.save()
        canceled_count += 1
        logger.info(f"Order {order.order_number} automatically canceled due to payment timeout")
    
    if canceled_count > 0:
        logger.info(f"Canceled {canceled_count} expired orders")
    
    return f"Canceled {canceled_count} expired orders"
