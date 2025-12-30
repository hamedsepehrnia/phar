"""
Template tags برای تبدیل تاریخ میلادی به شمسی
"""
from django import template
import jdatetime

register = template.Library()


@register.filter(name='jalali')
def jalali_date(value, format_str='%Y/%m/%d'):
    """
    تبدیل تاریخ میلادی به شمسی
    استفاده: {{ date|jalali }}
    با فرمت دلخواه: {{ date|jalali:"%Y/%m/%d - %H:%M" }}
    """
    if value is None:
        return ''
    
    try:
        if hasattr(value, 'date'):
            # اگر datetime باشد
            jalali = jdatetime.datetime.fromgregorian(datetime=value)
        else:
            # اگر فقط date باشد
            jalali = jdatetime.date.fromgregorian(date=value)
        
        return jalali.strftime(format_str)
    except Exception:
        return str(value)


@register.filter(name='jalali_full')
def jalali_full(value):
    """
    تبدیل تاریخ به شمسی با فرمت کامل
    مثال: ۲۹ آذر ۱۴۰۴ - ساعت ۱۴:۳۰
    """
    if value is None:
        return ''
    
    try:
        if hasattr(value, 'date'):
            jalali = jdatetime.datetime.fromgregorian(datetime=value)
            return jalali.strftime('%d %B %Y - ساعت %H:%M')
        else:
            jalali = jdatetime.date.fromgregorian(date=value)
            return jalali.strftime('%d %B %Y')
    except Exception:
        return str(value)


@register.filter(name='jalali_short')
def jalali_short(value):
    """
    تبدیل تاریخ به شمسی با فرمت کوتاه
    مثال: ۱۴۰۴/۰۹/۲۹
    """
    if value is None:
        return ''
    
    try:
        if hasattr(value, 'date'):
            jalali = jdatetime.datetime.fromgregorian(datetime=value)
        else:
            jalali = jdatetime.date.fromgregorian(date=value)
        return jalali.strftime('%Y/%m/%d')
    except Exception:
        return str(value)


@register.filter(name='jalali_datetime')
def jalali_datetime(value):
    """
    تبدیل تاریخ و ساعت به شمسی
    مثال: ۱۴۰۴/۰۹/۲۹ - ۱۴:۳۰
    """
    if value is None:
        return ''
    
    try:
        if hasattr(value, 'date'):
            jalali = jdatetime.datetime.fromgregorian(datetime=value)
            return jalali.strftime('%Y/%m/%d - %H:%M')
        else:
            jalali = jdatetime.date.fromgregorian(date=value)
            return jalali.strftime('%Y/%m/%d')
    except Exception:
        return str(value)
