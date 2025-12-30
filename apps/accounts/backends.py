"""
Authentication Backend برای ورود با شماره موبایل
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class PhoneAuthBackend(ModelBackend):
    """احراز هویت با شماره موبایل"""
    
    def authenticate(self, request, phone=None, **kwargs):
        """احراز هویت کاربر با شماره موبایل"""
        if phone is None:
            return None
        
        try:
            user = User.objects.get(phone=phone)
            if user.is_active:
                return user
        except User.DoesNotExist:
            return None
        
        return None
    
    def get_user(self, user_id):
        """دریافت کاربر با شناسه"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
