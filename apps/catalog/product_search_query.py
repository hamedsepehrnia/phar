"""
تبدیل نام فارسی محصولات داروخانه به عبارت جستجوی انگلیسی برای iHerb
"""
import re
import unicodedata

# نرمال‌سازی حروف عربی/فارسی
_CHAR_MAP = str.maketrans({
    'ي': 'ی', 'ك': 'ک', 'ة': 'ه', 'ؤ': 'و', 'إ': 'ا', 'أ': 'ا', 'آ': 'ا',
    '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
    '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
})

# عبارات چندکلمه‌ای (اولویت بالاتر)
_PHRASE_MAP = [
    ('ضدآفتاب', 'sunscreen'),
    ('ضدافتاب', 'sunscreen'),
    ('ضد افتاب', 'sunscreen'),
    ('ماسک مو', 'hair mask'),
    ('ماسک موي', 'hair mask'),
    ('ميسلارواتر', 'micellar water'),
    ('میسلار واتر', 'micellar water'),
    ('مولتی ویتامین', 'multivitamin'),
    ('مولتي ويتامين', 'multivitamin'),
    ('دورچشم', 'eye cream'),
    ('دور چشم', 'eye cream'),
    ('خمیردندان', 'toothpaste'),
    ('خميردندان', 'toothpaste'),
    ('دهانشویه', 'mouthwash'),
    ('دهانشويه', 'mouthwash'),
    ('بی بی', 'bb cream'),
    ('بي بي', 'bb cream'),
    ('امگا 3', 'omega 3'),
    ('امگا3', 'omega 3'),
    ('امگا ۳', 'omega 3'),
    ('ال کارنیتین', 'l-carnitine'),
    ('ال کارنيتين', 'l-carnitine'),
    ('زبان شور', 'mouth freshener spray'),
    ('بیوتین', 'biotin'),
    ('بيوتين', 'biotin'),
    ('گلوتاتیون', 'glutathione'),
    ('گلوتاتيون', 'glutathione'),
    ('هیالورونیک', 'hyaluronic acid'),
    ('هيالورون', 'hyaluronic acid'),
    ('کلاژن', 'collagen'),
    ('پروبیوتیک', 'probiotic'),
    ('پروبيوتيک', 'probiotic'),
]

_WORD_MAP = {
    'قرص': 'tablet', 'کپسول': 'capsule', 'شربت': 'syrup', 'قطره': 'drops',
    'ساشه': 'sachet', 'پودر': 'powder', 'آمپول': 'ampoule', 'ویال': 'vial',
    'ويال': 'vial', 'پرل': 'softgel', 'انشور': 'ensure',
    'کرم': 'cream', 'ژل': 'gel', 'لوسيون': 'lotion', 'لوسیون': 'lotion',
    'پماد': 'ointment', 'سرم': 'serum', 'تونر': 'toner', 'اسپری': 'spray',
    'اسپري': 'spray', 'فوم': 'foam', 'پن': 'bar soap',
    'شامپو': 'shampoo', 'ماسک': 'mask', 'روغن': 'oil', 'صابون': 'soap',
    'مسواک': 'toothbrush', 'دئودورانت': 'deodorant', 'رژ': 'lipstick',
    'ریمل': 'mascara', 'بالم': 'balm', 'خط': 'liner', 'چشم': 'eye',
    'ضد': 'anti', 'مرطوب': 'moisturizer', 'ابرسان': 'hydrating',
    'ترمیم': 'repair', 'ترميم': 'repair', 'ضدچروک': 'anti wrinkle',
    'ضدریزش': 'anti hair loss', 'ضدريزش': 'anti hair loss',
    'پوست': 'skin', 'مو': 'hair', 'موي': 'hair', 'بدن': 'body',
    'صورت': 'face', 'دندان': 'dental', 'لب': 'lip',
    'چرب': 'oily', 'خشک': 'dry', 'خشك': 'dry', 'حساس': 'sensitive',
    'رنگی': 'tinted', 'رنگي': 'tinted', 'رنگ': 'color',
    'روشن': 'brightening', 'سفید': 'whitening', 'سفيد': 'whitening',
    'کودک': 'kids', 'کيدز': 'kids', 'کیندر': 'kids', 'کيندر': 'kids',
    'بانوان': 'women', 'اقايان': 'men', 'آقایان': 'men',
    'ويتامين': 'vitamin', 'ویتامین': 'vitamin', 'ويت': 'vitamin',
    'مولتي': 'multi', 'مولتی': 'multi', 'پلاس': 'plus',
    'زينک': 'zinc', 'زینک': 'zinc', 'منيزيم': 'magnesium', 'منیزیم': 'magnesium',
    'کلسیم': 'calcium', 'کلسيم': 'calcium', 'آهن': 'iron', 'ث': 'vitamin c',
    'امگا': 'omega', 'پروتئین': 'protein', 'پروتئين': 'protein',
    'شستشو': 'wash', 'شستشوي': 'wash', 'پاک': 'cleanser', 'کننده': '',
    'محلول': 'solution', 'قرص': 'tablet', 'جوشان': 'effervescent',
    'مکمل': 'supplement', 'گیاهی': 'herbal', 'گياهي': 'herbal',
    'لاغری': 'weight loss', 'لاغري': 'weight loss', 'اسلیم': 'slim',
    'اسليم': 'slim', 'مام': 'roll on', 'استیک': 'stick', 'استيک': 'stick',
    'عددی': '', 'عددي': '', 'عدد': '', 'قیمت': '', 'قيمت': '', 'جدید': '',
    'جديد': '', 'انواع': '', 'ميلي': 'mg', 'میلی': 'mg', 'م': 'mg',
    'گرم': 'g', 'میل': 'ml', 'ميل': 'ml', 'لیتر': 'l',
    'و': 'and', 'برای': 'for', 'با': 'with',
}

# برندهای رایج — برای fallback بدون برند
_KNOWN_BRANDS = {
    'يوروويتال', 'یوروویتال', 'باريج', 'باریج', 'گلدن', 'لايف', 'life',
    'سريتا', 'serita', 'پريم', 'prim', 'بيول', 'biol', 'سيگنال', 'signal',
    'ميسويک', 'meswak', 'اويدرم', 'oviderm', 'هيدرودرم', 'hydroderm',
    'درماليفت', 'dermalift', 'ويتالير', 'vitalayer', 'نوتراکس', 'nutrax',
    'کانديد', 'candid', 'نوپريت', 'نواکنه', 'کامان', 'لافارر', 'گلمر',
    'ادرا', 'adara', 'اريکه', 'erike', 'رويوال', 'royal', 'کاپوس', 'capus',
    'ژيلت', 'gillette', 'کلوزاپ', 'closeup', 'فوکس', 'fuchs', 'رکسونا',
    'rexona', 'دیپ', 'dip', 'سنس', 'sense', '2080', 'اردن', 'jordan',
}

# نگاشت آوانگاری برند/کلمه فارسی → لاتین
_TRANSLIT_MAP = {
    'يوروويتال': 'eurovital', 'باريج': 'barij', 'گلدن': 'golden',
    'لايف': 'life', 'سريتا': 'serita', 'پريم': 'prim', 'بيول': 'biol',
    'سيگنال': 'signal', 'ميسويک': 'meswak', 'اويدرم': 'oviderm',
    'هيدرودرم': 'hydroderm', 'درماليفt': 'dermalift', 'ويتالير': 'vitalayer',
    'نوتراکس': 'nutrax', 'کانديد': 'candid', 'زينک': 'zinc', 'منيزيم': 'magnesium',
    'هيربيوتي': 'hair biotin', 'هيرونيک': 'hironic', 'يوني': 'uni',
    'يونيزينک': 'uni zinc', 'اپتي': 'opti', 'اپتايزر': 'optimizer',
    'اترومد': 'etromed', 'ادرا': 'adara', 'ارومکس': 'aromax',
    'اسليم': 'slim', 'اسکين': 'skin', 'برايت': 'bright', 'مکس': 'max',
    'فورت': 'forte', 'هلث': 'health', 'ايد': 'aid', 'دي': 'd',
    'پدي': 'pedi', 'کيو': 'q', 'اف': 'eff', 'ث': 'c',
}

# کلمات توقف — در fallback حذف می‌شوند
_STOP_WORDS = {'and', 'with', 'for', 'the', 'of', 'mg', 'ml', 'g', ''}


def normalize_persian(text: str) -> str:
    text = unicodedata.normalize('NFKC', text or '')
    text = text.translate(_CHAR_MAP)
    text = re.sub(r'[_\-–—]+', ' ', text)
    text = re.sub(r'\([^)]*\)', ' ', text)
    text = re.sub(r'\d+[\.,]?\d*\s*(عدد[یي]?|عددي|عدد)', ' ', text)
    text = re.sub(r'\b\d{3,}\b', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def _transliterate_token(token: str) -> str:
    lower = token.lower()
    if lower in _TRANSLIT_MAP:
        return _TRANSLIT_MAP[lower]
    if re.fullmatch(r'[a-zA-Z0-9+\.]+', token):
        return token.lower()
    return ''


def persian_to_english_query(name: str) -> str:
    """تبدیل نام فارسی به عبارت جستجوی انگلیسی."""
    text = normalize_persian(name)

    # ویتامین‌های ترکیبی: ا+d3+ک2
    text = re.sub(r'\bا\s*\+\s*د\s*3\b', 'vitamin a d3', text, flags=re.I)
    text = re.sub(r'\bد\s*3\b', 'vitamin d3', text, flags=re.I)
    text = re.sub(r'\bک\s*2\b', 'vitamin k2', text, flags=re.I)
    text = re.sub(r'\bکا\s*2\b', 'vitamin k2', text, flags=re.I)
    text = re.sub(r'\bب\s*12\b', 'vitamin b12', text, flags=re.I)
    text = re.sub(r'\bب\s*6\b', 'vitamin b6', text, flags=re.I)
    text = re.sub(r'\b\+', ' ', text)

    for fa, en in _PHRASE_MAP:
        text = text.replace(fa, f' {en} ')

    tokens = re.split(r'[\s+]+', text)
    english_tokens = []

    for token in tokens:
        token = token.strip('.,')
        if not token:
            continue

        if re.fullmatch(r'[\d\.]+', token):
            continue

        # 15mg, 1000m, d3
        m = re.match(r'^(\d+)\s*(mg|ml|g|mcg)?$', token, re.I)
        if m:
            unit = m.group(2) or 'mg'
            english_tokens.append(f'{m.group(1)}{unit.lower()}')
            continue
        m = re.match(r'^([a-zA-Z]\d+|[a-zA-Z]\+?[a-zA-Z]?|[a-zA-Z]{2,})$', token, re.I)
        if m:
            english_tokens.append(token.lower())
            continue

        if token in {'ا', 'اي'}:
            english_tokens.append('vitamin a')
            continue
        if token in {'د', 'دي'}:
            english_tokens.append('vitamin d')
            continue
        if token in {'ب', 'بي'} and len(tokens) > 1:
            english_tokens.append('b')
            continue

        if token in _WORD_MAP:
            en = _WORD_MAP[token]
            if en:
                english_tokens.append(en)
            continue

        tr = _transliterate_token(token)
        if tr:
            english_tokens.extend(tr.split())

    query = ' '.join(english_tokens)
    query = re.sub(r'\bmg mg\b', 'mg', query)
    query = re.sub(r'\s+', ' ', query).strip()
    return query


def build_search_queries(name: str) -> list[str]:
    """
    چند عبارت جستجو به ترتیب اولویت:
    1. ترجمه کامل
    2. بدون برند (اولین کلمه)
    3. فقط نوع محصول + ماده فعال
    """
    queries = []
    full = persian_to_english_query(name)
    if full and len(full.split()) >= 2:
        queries.append(full)
    elif full:
        queries.append(full)

    tokens = full.split()
    if len(tokens) > 2:
        without_brand = ' '.join(tokens[1:])
        if without_brand and len(without_brand.split()) >= 2 and without_brand not in queries:
            queries.append(without_brand)

    # fallback: نوع محصول + ۱-۲ کلمه کلیدی
    product_types = {
        'capsule', 'tablet', 'syrup', 'drops', 'sachet', 'cream', 'gel',
        'shampoo', 'serum', 'sunscreen', 'toothpaste', 'toothbrush',
        'soap', 'vitamin', 'supplement', 'softgel', 'mouthwash', 'oil',
        'mask', 'deodorant', 'moisturizer', 'lotion', 'toner',
    }
    key_tokens = [t for t in tokens if t in product_types or t in {
        'zinc', 'biotin', 'collagen', 'omega', 'magnesium', 'calcium',
        'iron', 'multivitamin', 'probiotic', 'hyaluronic', 'acid',
        'anti', 'hair', 'skin', 'kids', 'd3', 'c',
    }]
    if key_tokens and len(key_tokens) >= 2:
        generic = ' '.join(dict.fromkeys(key_tokens))
        if generic and generic not in queries:
            queries.append(generic)

    return queries[:4] or [full] if full else ['health supplement']
