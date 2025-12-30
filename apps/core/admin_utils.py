"""
توابع کمکی برای پنل ادمین
"""
import jdatetime


def jalali_date(date_value, show_time=True):
    """
    تبدیل تاریخ میلادی به شمسی
    
    Args:
        date_value: تاریخ میلادی (datetime یا date)
        show_time: نمایش ساعت و دقیقه
    
    Returns:
        رشته تاریخ شمسی
    """
    if date_value is None:
        return '-'
    try:
        if hasattr(date_value, 'hour'):
            jalali = jdatetime.datetime.fromgregorian(datetime=date_value)
            if show_time:
                return jalali.strftime('%Y/%m/%d - %H:%M')
        else:
            jalali = jdatetime.date.fromgregorian(date=date_value)
        return jalali.strftime('%Y/%m/%d')
    except Exception:
        return str(date_value)


def jalali_date_short(date_value):
    """تاریخ شمسی بدون ساعت"""
    return jalali_date(date_value, show_time=False)
