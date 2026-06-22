"""مقادیر پیش‌فرض سایت — وقتی در دیتابیس خالی باشد."""

DEFAULT_PHONE = '03132344707'
DEFAULT_ADDRESS = 'اصفهان - شهر اصفهان-خیابان طیب - روبروی کاخ زبان.'
DEFAULT_MAP_LATITUDE = 32.660282
DEFAULT_MAP_LONGITUDE = 51.666233
DEFAULT_MAP_ZOOM = 14

DEFAULT_ABOUT_SHORT = (
    'بیش از ۷ سال سابقه در ارائه خدمات دارویی و سلامت؛ '
    'دسترسی آسان، مطمئن و سریع به محصولات بهداشتی و دارویی.'
)

DEFAULT_ABOUT_PARAGRAPHS = [
    'ما فعالیت خود را از سال ۱۳۹۸ آغاز کرده‌ایم و با بیش از ۷ سال سابقه در ارائه خدمات دارویی و سلامت، همواره تلاش کرده‌ایم تا دسترسی به محصولات بهداشتی، مراقبتی، مکمل‌های غذایی و دارویی را برای هم‌وطنان عزیز آسان‌تر، مطمئن‌تر و سریع‌تر کنیم.',
    'این مجموعه توسط دکتر عارفه واعظی داروساز و فارغ‌التحصیل دانشگاه اصفهان در سال ۱۳۹۴ تأسیس و مدیریت می‌شود. هدف ما از راه‌اندازی این فروشگاه اینترنتی، ارائه محصولات اصیل و باکیفیت همراه با مشاوره تخصصی و خدماتی است که شایسته اعتماد شما باشد.',
    'داروخانه ما در اصفهان، خیابان طیب، ساختمان افتاب واقع شده و به صورت حضوری و آنلاین آماده ارائه خدمات به مشتریان است.',
    'تمامی محصولات پیش از بسته‌بندی و ارسال، توسط داروساز از نظر اصالت، سلامت ظاهری، تاریخ انقضا و شرایط نگهداری بررسی می‌شوند تا سفارش شما با اطمینان کامل به دستتان برسد.',
    'در طول سال، به مناسبت‌های مختلف، جشنواره‌های فروش، تخفیف‌های ویژه و پیشنهادهای اختصاصی برای مشتریان در نظر گرفته می‌شود تا بتوانید محصولات مورد نیاز خود را با بهترین قیمت تهیه کنید.',
    'امکان ارسال سفارش به سراسر کشور فراهم است و تلاش می‌کنیم سفارش‌ها در کوتاه‌ترین زمان ممکن، با بسته‌بندی مناسب و ایمن به دست شما برسند.',
    'اعتماد شما ارزشمندترین سرمایه ماست و امیدواریم با ارائه خدماتی حرفه‌ای، تجربه‌ای مطمئن و رضایت‌بخش از خرید آنلاین محصولات سلامت برایتان فراهم کنیم.',
]

SITE_SETTING_DEFAULTS = {
    'phone': DEFAULT_PHONE,
    'address': DEFAULT_ADDRESS,
    'map_latitude': DEFAULT_MAP_LATITUDE,
    'map_longitude': DEFAULT_MAP_LONGITUDE,
    'map_zoom': DEFAULT_MAP_ZOOM,
    'about_short': DEFAULT_ABOUT_SHORT,
}


class SiteSettingsProxy:
    """Wrap SiteSettings and fall back to defaults for empty values."""

    def __init__(self, settings):
        self._settings = settings

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        if self._settings is not None and hasattr(self._settings, name):
            value = getattr(self._settings, name)
            if value not in (None, ''):
                return value
        if name in SITE_SETTING_DEFAULTS:
            return SITE_SETTING_DEFAULTS[name]
        if self._settings is not None:
            return getattr(self._settings, name, '')
        return SITE_SETTING_DEFAULTS.get(name, '')

    @property
    def about_paragraphs(self):
        if self._settings and getattr(self._settings, 'about_content', None):
            return None
        return DEFAULT_ABOUT_PARAGRAPHS

    @property
    def whatsapp_link(self):
        whatsapp = ''
        if self._settings is not None:
            whatsapp = getattr(self._settings, 'whatsapp', '') or ''
        if whatsapp.startswith('http'):
            return whatsapp
        if whatsapp:
            digits = ''.join(ch for ch in whatsapp if ch.isdigit())
            if digits:
                if digits.startswith('0'):
                    digits = '98' + digits[1:]
                return f'https://wa.me/{digits}'
        return ''

    @property
    def has_custom_about(self):
        return bool(self._settings and getattr(self._settings, 'about_content', None))
