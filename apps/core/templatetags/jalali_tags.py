"""
Template tags برای تبدیل تاریخ میلادی به شمسی
"""
from django import template

from apps.core.jalali_utils import to_jalali_datetime

register = template.Library()


@register.filter(name='jalali')
def jalali_date(value, format_str='%Y/%m/%d'):
    return to_jalali_datetime(value, format_str)


@register.filter(name='jalali_full')
def jalali_full(value):
    return to_jalali_datetime(value, '%d %B %Y - ساعت %H:%M')


@register.filter(name='jalali_short')
def jalali_short(value):
    return to_jalali_datetime(value, '%Y/%m/%d')


@register.filter(name='jalali_datetime')
def jalali_datetime(value):
    return to_jalali_datetime(value, '%Y/%m/%d - %H:%M')
