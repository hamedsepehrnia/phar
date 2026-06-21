"""
سرویس ارسال پیامک با استفاده از MsgWay
"""
import json
import logging
import requests
from django.conf import settings
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


class MsgWayService:
    """سرویس ارسال پیامک MsgWay"""
    
    BASE_URL = "https://api.msgway.com/send"
    
    @classmethod
    def get_api_key(cls) -> str:
        """دریافت کلید API از تنظیمات"""
        return getattr(settings, 'MSGWAY_API_KEY', '')
    
    @classmethod
    def get_accept_language(cls) -> str:
        """دریافت زبان از تنظیمات"""
        return getattr(settings, 'MSGWAY_ACCEPT_LANGUAGE', 'fa')
    
    @classmethod
    def is_configured(cls) -> bool:
        """بررسی اینکه آیا سرویس پیکربندی شده است"""
        return bool(cls.get_api_key())
    
    @classmethod
    def send_templated_sms(
        cls,
        receptor: str,
        template_id: int,
        params: Optional[List[str]] = None,
        method: str = "sms",
        code: Optional[str] = None,
        expire_time: Optional[int] = None,
        provider: Optional[int] = None,
        length: Optional[int] = None,
        hash_value: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        ارسال پیامک با قالب
        
        Args:
            receptor: شماره گیرنده (مثلاً 09123456789)
            template_id: شناسه قالب در پنل MsgWay
            params: آرایه پارامترها (حداکثر ۱۰ مورد)
            method: متد ارسال (sms, ivr, smart, messenger)
            code: کد تأیید (برای OTP، حداقل ۳ و حداکثر ۱۲ کاراکتر)
            expire_time: مدت اعتبار کد به ثانیه
            provider: شماره اپراتور (1=مگفا, 2=آتیه, 3=آسیاتک, 5=ارمغان)
            length: تعداد کاراکتر برای ایجاد خودکار کد/رمز
            hash_value: رشته hash برای تشخیص خودکار پیامک
            
        Returns:
            dict با کلیدهای success و message
        """
        if not cls.is_configured():
            logger.warning("سرویس پیامک MsgWay پیکربندی نشده است")
            return {
                'success': False,
                'message': 'سرویس پیامک پیکربندی نشده است'
            }
        
        # در حالت DEBUG و SMS_LOG_ONLY فقط لاگ می‌کنیم
        if settings.DEBUG and getattr(settings, 'SMS_LOG_ONLY', False):
            logger.info(
                f"[DEBUG SMS] به {receptor}: "
                f"template={template_id}, params={params}"
            )
            return {
                'success': True,
                'message': 'پیامک در حالت DEBUG ارسال نشد (فقط لاگ شد)'
            }
        
        try:
            # ساخت body مطابق مستندات
            body = {
                'mobile': receptor,
                'method': method,
                'templateID': template_id,
            }
            
            if params:
                body['params'] = params[:10]  # حداکثر ۱۰ پارامتر
            
            if code:
                body['code'] = str(code)[:12]  # حداکثر ۱۲ کاراکتر
            
            if expire_time:
                body['expireTime'] = int(expire_time)
            
            if provider and provider in [1, 2, 3, 5]:
                body['provider'] = int(provider)
            
            if length:
                body['length'] = int(length)
            
            if hash_value:
                body['hash'] = str(hash_value)
            
            # ارسال درخواست مطابق نمونه مستندات
            headers = {
                'apiKey': cls.get_api_key(),
                'accept-language': cls.get_accept_language(),
                'Content-Type': 'application/json',
            }
            
            response = requests.post(
                cls.BASE_URL,
                headers=headers,
                data=json.dumps(body),
                timeout=10
            )
            
            result = response.json()
            
            if result.get('status') == 'success':
                logger.info(
                    f"پیامک با موفقیت به {receptor} ارسال شد "
                    f"(ref: {result.get('referenceID')})"
                )
                return {
                    'success': True,
                    'message': 'پیامک با موفقیت ارسال شد',
                    'data': result,
                    'reference_id': result.get('referenceID'),
                }
            else:
                error_msg = result.get('error', {}).get('message', 'خطای نامشخص')
                error_code = result.get('error', {}).get('code', '')
                logger.error(
                    f"خطا در ارسال پیامک به {receptor}: "
                    f"[{error_code}] {error_msg}"
                )
                return {
                    'success': False,
                    'message': error_msg,
                    'error_code': error_code,
                    'data': result,
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
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"خطا در پردازش پاسخ از MsgWay: {e}")
            return {
                'success': False,
                'message': f'خطا در پردازش پاسخ: {str(e)}'
            }
        except Exception as e:
            logger.error(f"خطای غیرمنتظره در ارسال پیامک به {receptor}: {e}")
            return {
                'success': False,
                'message': f'خطای غیرمنتظره: {str(e)}'
            }


# ============================================================================
# توابع کمکی
# ============================================================================

def send_otp_sms(phone: str, code: str) -> dict:
    """
    ارسال پیامک کد تایید
    قالب در پنل MsgWay: "کد تایید شما: [param1]"
    """
    template_id = getattr(settings, 'MSGWAY_OTP_TEMPLATE_ID', 0)
    
    if not template_id:
        logger.error("MSGWAY_OTP_TEMPLATE_ID تنظیم نشده است")
        return {'success': False, 'message': 'شناسه قالب OTP تنظیم نشده است'}
    
    expire_time = getattr(settings, 'OTP_EXPIRE_SECONDS', 300)
    
    return MsgWayService.send_templated_sms(
        receptor=phone,
        template_id=template_id,
        params=[code],
        code=code,
        expire_time=expire_time,
    )


def send_order_status_sms(
    phone: str,
    customer_name: str,
    product_name: str,
    old_status: str,
    new_status: str
) -> dict:
    """
    ارسال پیامک تغییر وضعیت سفارش
    قالب در پنل MsgWay: 
    "[param1] عزیز، وضعیت سفارش شما برای محصول «[param2]» از «[param3]» به «[param4]» تغییر کرد."
    """
    template_id = getattr(settings, 'MSGWAY_ORDER_STATUS_TEMPLATE_ID', 0)
    
    if not template_id:
        logger.error("MSGWAY_ORDER_STATUS_TEMPLATE_ID تنظیم نشده است")
        return {'success': False, 'message': 'شناسه قالب تغییر وضعیت سفارش تنظیم نشده است'}
    
    return MsgWayService.send_templated_sms(
        receptor=phone,
        template_id=template_id,
        params=[customer_name, product_name, old_status, new_status],
    )


def send_welcome_sms(phone: str, name: str) -> dict:
    """
    ارسال پیامک خوش‌آمدگویی
    قالب در پنل MsgWay: "[param1] عزیز، به داواژو خوش آمدید!"
    """
    template_id = getattr(settings, 'MSGWAY_WELCOME_TEMPLATE_ID', 0)
    
    if not template_id:
        logger.error("MSGWAY_WELCOME_TEMPLATE_ID تنظیم نشده است")
        return {'success': False, 'message': 'شناسه قالب خوش‌آمدگویی تنظیم نشده است'}
    
    return MsgWayService.send_templated_sms(
        receptor=phone,
        template_id=template_id,
        params=[name],
    )


def send_payment_success_sms(phone: str, customer_name: str, order_number: str) -> dict:
    """
    ارسال پیامک تایید پرداخت
    قالب در پنل MsgWay: 
    "[param1] عزیز، پرداخت سفارش شماره [param2] با موفقیت انجام شد. با تشکر از خرید شما - داروخانه دکتر واعظی"
    """
    template_id = getattr(settings, 'MSGWAY_PAYMENT_SUCCESS_TEMPLATE_ID', 0)
    
    if not template_id:
        logger.error("MSGWAY_PAYMENT_SUCCESS_TEMPLATE_ID تنظیم نشده است")
        return {'success': False, 'message': 'شناسه قالب تایید پرداخت تنظیم نشده است'}
    
    return MsgWayService.send_templated_sms(
        receptor=phone,
        template_id=template_id,
        params=[customer_name, order_number],
    )