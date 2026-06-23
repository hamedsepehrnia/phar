"""تبدیل تاریخ میلادی به شمسی با در نظر گرفتن منطقه زمانی سایت."""
import jdatetime
from django.utils import timezone as dj_timezone


def to_local_naive_datetime(value):
    if value is None:
        return None
    if not hasattr(value, 'hour'):
        return value
    if dj_timezone.is_aware(value):
        value = dj_timezone.localtime(value)
    return value.replace(tzinfo=None)


def to_jalali_datetime(value, format_str='%Y/%m/%d - %H:%M'):
    if value is None:
        return ''
    try:
        if hasattr(value, 'hour'):
            local_value = to_local_naive_datetime(value)
            jalali = jdatetime.datetime.fromgregorian(datetime=local_value)
            return jalali.strftime(format_str)
        jalali = jdatetime.date.fromgregorian(date=value)
        return jalali.strftime(format_str)
    except Exception:
        return str(value)
