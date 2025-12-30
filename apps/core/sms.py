"""
سرویس ارسال پیامک با استفاده از Kavenegar
"""
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class KavenegarService:
    """سرویس ارسال پیامک کاوه‌نگار"""
    
    BASE_URL = "https://api.kavenegar.com/v1/{api_key}/sms/send.json"
    
    @classmethod
    def get_api_key(cls):
        """دریافت کلید API از تنظیمات"""
        return getattr(settings, 'SMS_API_KEY', '')
    
    @classmethod
    def get_sender(cls):
        """دریافت شماره فرستنده از تنظیمات"""
        return getattr(settings, 'SMS_SENDER', '')
    
    @classmethod
    def is_configured(cls):
        """بررسی اینکه آیا سرویس پیکربندی شده است"""
        return bool(cls.get_api_key()) and bool(cls.get_sender())
    
    @classmethod
    def send_sms(cls, receptor: str, message: str) -> dict:
        """
        ارسال پیامک
        
        Args:
            receptor: شماره گیرنده (مثلاً 09123456789)
            message: متن پیامک
            
        Returns:
            dict با کلیدهای success و message
        """
        if not cls.is_configured():
            logger.warning("سرویس پیامک پیکربندی نشده است")
            return {
                'success': False,
                'message': 'سرویس پیامک پیکربندی نشده است'
            }
        
        # در حالت DEBUG فقط لاگ می‌کنیم
        if settings.DEBUG:
            logger.info(f"[DEBUG SMS] به {receptor}: {message}")
            return {
                'success': True,
                'message': 'پیامک در حالت DEBUG ارسال نشد (فقط لاگ شد)'
            }
        
        try:
            url = cls.BASE_URL.format(api_key=cls.get_api_key())
            
            data = {
                'receptor': receptor,
                'message': message,
                'sender': cls.get_sender()
            }
            
            response = requests.post(url, data=data, timeout=30)
            result = response.json()
            
            if result.get('return', {}).get('status') == 200:
                logger.info(f"پیامک با موفقیت به {receptor} ارسال شد")
                return {
                    'success': True,
                    'message': 'پیامک با موفقیت ارسال شد',
                    'data': result
                }
            else:
                error_msg = result.get('return', {}).get('message', 'خطای نامشخص')
                logger.error(f"خطا در ارسال پیامک به {receptor}: {error_msg}")
                return {
                    'success': False,
                    'message': error_msg,
                    'data': result
                }
                
        except requests.Timeout:
            logger.error(f"Timeout در ارسال پیامک به {receptor}")
            return {
                'success': False,
                'message': 'خطای Timeout در اتصال به سرویس پیامک'
            }
        except requests.RequestException as e:
            logger.error(f"خطای شبکه در ارسال پیامک به {receptor}: {e}")
            return {
                'success': False,
                'message': f'خطای شبکه: {str(e)}'
            }
        except Exception as e:
            logger.error(f"خطای غیرمنتظره در ارسال پیامک به {receptor}: {e}")
            return {
                'success': False,
                'message': f'خطای غیرمنتظره: {str(e)}'
            }


# توابع کمکی برای استفاده آسان‌تر

def send_otp_sms(phone: str, code: str) -> dict:
    """ارسال پیامک کد تایید"""
    message = f"کد تایید شما: {code}\nداواژو"
    return KavenegarService.send_sms(phone, message)


def send_order_status_sms(phone: str, customer_name: str, product_name: str, 
                          old_status: str, new_status: str) -> dict:
    """ارسال پیامک تغییر وضعیت سفارش"""
    message = (
        f"{customer_name} عزیز،\n"
        f"وضعیت سفارش شما برای محصول «{product_name}» "
        f"از «{old_status}» به «{new_status}» تغییر کرد.\n"
        f"داواژو"
    )
    return KavenegarService.send_sms(phone, message)


def send_welcome_sms(phone: str, name: str) -> dict:
    """ارسال پیامک خوش‌آمدگویی"""
    message = f"{name} عزیز، به داواژو خوش آمدید!\nداواژو"
    return KavenegarService.send_sms(phone, message)


def send_payment_success_sms(phone: str, customer_name: str, order_number: str) -> dict:
    """ارسال پیامک تایید پرداخت"""
    message = (
        f"{customer_name} عزیز،\n"
        f"پرداخت سفارش شماره {order_number} با موفقیت انجام شد.\n"
        f"با تشکر از خرید شما - داواژو"
    )
    return KavenegarService.send_sms(phone, message)
