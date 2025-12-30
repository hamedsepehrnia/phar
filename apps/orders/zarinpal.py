"""
سرویس پرداخت زرین‌پال
"""
import logging
import requests
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)


class ZarinPalService:
    """سرویس درگاه پرداخت زرین‌پال"""
    
    # Sandbox URLs
    SANDBOX_REQUEST_URL = 'https://sandbox.zarinpal.com/pg/v4/payment/request.json'
    SANDBOX_VERIFY_URL = 'https://sandbox.zarinpal.com/pg/v4/payment/verify.json'
    SANDBOX_STARTPAY_URL = 'https://sandbox.zarinpal.com/pg/StartPay/'
    
    # Production URLs
    PRODUCTION_REQUEST_URL = 'https://api.zarinpal.com/pg/v4/payment/request.json'
    PRODUCTION_VERIFY_URL = 'https://api.zarinpal.com/pg/v4/payment/verify.json'
    PRODUCTION_STARTPAY_URL = 'https://www.zarinpal.com/pg/StartPay/'
    
    @classmethod
    def get_merchant_id(cls):
        """دریافت merchant_id از تنظیمات"""
        merchant_id = getattr(settings, 'ZARINPAL_MERCHANT_ID', '')
        if not merchant_id or merchant_id == 'your-merchant-id':
            # استفاده از merchant_id تستی زرین‌پال برای sandbox
            if cls.is_sandbox():
                return 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'  # برای sandbox هر مقداری قبول میشه
        return merchant_id
    
    @classmethod
    def is_sandbox(cls):
        """آیا حالت sandbox فعال است"""
        return getattr(settings, 'ZARINPAL_SANDBOX', True)
    
    @classmethod
    def get_urls(cls):
        """دریافت URLهای API"""
        if cls.is_sandbox():
            return {
                'request': cls.SANDBOX_REQUEST_URL,
                'verify': cls.SANDBOX_VERIFY_URL,
                'startpay': cls.SANDBOX_STARTPAY_URL,
            }
        return {
            'request': cls.PRODUCTION_REQUEST_URL,
            'verify': cls.PRODUCTION_VERIFY_URL,
            'startpay': cls.PRODUCTION_STARTPAY_URL,
        }
    
    @classmethod
    def create_payment(cls, order, callback_url):
        """
        ایجاد درخواست پرداخت
        """
        urls = cls.get_urls()
        merchant_id = cls.get_merchant_id()
        
        data = {
            'merchant_id': merchant_id,
            'amount': int(order.total) * 10,  # تبدیل به ریال
            'description': f'پرداخت سفارش {order.order_number}',
            'callback_url': callback_url,
            'metadata': {
                'mobile': order.receiver_phone,
                'order_id': order.order_number,
            }
        }
        
        logger.info(f"ZarinPal Payment Request - Order: {order.order_number}, Amount: {data['amount']}, Callback: {callback_url}")
        
        try:
            response = requests.post(urls['request'], json=data, timeout=10)
            logger.info(f"ZarinPal Response Status: {response.status_code}")
            result = response.json()
            logger.info(f"ZarinPal Response: {result}")
            
            if result.get('data') and result['data'].get('authority'):
                authority = result['data']['authority']
                payment_url = f"{urls['startpay']}{authority}"
                logger.info(f"ZarinPal Payment URL: {payment_url}")
                return {
                    'success': True,
                    'authority': authority,
                    'payment_url': payment_url,
                }
            else:
                errors = result.get('errors', {})
                message = errors.get('message', 'خطا در ایجاد درخواست پرداخت')
                logger.error(f"ZarinPal Error: {errors}")
                return {
                    'success': False,
                    'message': message,
                    'errors': errors,
                }
        except requests.RequestException as e:
            logger.exception(f"ZarinPal Connection Error: {e}")
            return {
                'success': False,
                'message': 'خطا در اتصال به درگاه پرداخت',
                'errors': str(e),
            }
    
    @classmethod
    def verify_payment(cls, authority, amount):
        """
        تایید پرداخت
        """
        urls = cls.get_urls()
        merchant_id = cls.get_merchant_id()
        
        data = {
            'merchant_id': merchant_id,
            'authority': authority,
            'amount': int(amount) * 10,  # تبدیل به ریال
        }
        
        logger.info(f"ZarinPal Verify Request - Authority: {authority}, Amount: {data['amount']}")
        
        try:
            response = requests.post(urls['verify'], json=data, timeout=10)
            logger.info(f"ZarinPal Verify Response Status: {response.status_code}")
            result = response.json()
            logger.info(f"ZarinPal Verify Response: {result}")
            
            if result.get('data') and result['data'].get('code') == 100:
                logger.info(f"ZarinPal Payment Verified Successfully - RefID: {result['data']['ref_id']}")
                return {
                    'success': True,
                    'ref_id': str(result['data']['ref_id']),
                    'card_pan': result['data'].get('card_pan', ''),
                    'fee': result['data'].get('fee', 0),
                }
            elif result.get('data') and result['data'].get('code') == 101:
                # تراکنش قبلاً تایید شده
                logger.info(f"ZarinPal Payment Already Verified - RefID: {result['data']['ref_id']}")
                return {
                    'success': True,
                    'ref_id': str(result['data']['ref_id']),
                    'already_verified': True,
                }
            else:
                errors = result.get('errors', {})
                logger.error(f"ZarinPal Verify Error: {errors}")
                return {
                    'success': False,
                    'message': errors.get('message', 'تایید پرداخت ناموفق'),
                    'code': result.get('data', {}).get('code'),
                }
        except requests.RequestException as e:
            logger.exception(f"ZarinPal Verify Connection Error: {e}")
            return {
                'success': False,
                'message': 'خطا در تایید پرداخت',
                'errors': str(e),
            }
