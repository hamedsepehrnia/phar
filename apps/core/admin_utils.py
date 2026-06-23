"""
توابع کمکی برای پنل ادمین
"""
from apps.core.jalali_utils import to_jalali_datetime


def jalali_date(date_value, show_time=True):
    if date_value is None:
        return '-'
    if show_time and hasattr(date_value, 'hour'):
        return to_jalali_datetime(date_value, '%Y/%m/%d - %H:%M')
    return to_jalali_datetime(date_value, '%Y/%m/%d')


def jalali_date_short(date_value):
    """تاریخ شمسی بدون ساعت"""
    return jalali_date(date_value, show_time=False)
