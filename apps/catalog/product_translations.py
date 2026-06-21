"""
مدیریت ترجمه انگلیسی محصولات (منبع اصلی جستجوی تصویر)
"""
import hashlib
import json
from pathlib import Path

import xlrd
from django.conf import settings
from openpyxl import Workbook

DEFAULT_TRANSLATIONS_PATH = Path(settings.BASE_DIR) / 'data' / 'seed' / 'product_translations.json'
DEFAULT_ENRICHED_XLSX = Path(settings.BASE_DIR) / 'سایت-en.xlsx'
DEFAULT_SOURCE_XLS = Path(settings.BASE_DIR) / 'سایت.Xls'


def product_name_key(name: str) -> str:
    return hashlib.sha256(name.strip().encode('utf-8')).hexdigest()[:16]


def load_translations(path: Path | None = None) -> dict:
    path = path or DEFAULT_TRANSLATIONS_PATH
    if not path.exists():
        return {'version': 1, 'products': {}}
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


def save_translations(data: dict, path: Path | None = None):
    path = path or DEFAULT_TRANSLATIONS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def read_source_rows(xls_path: Path | None = None) -> list[dict]:
    """خواندن ردیف‌های اکسل: price, name_fa"""
    xls_path = xls_path or DEFAULT_SOURCE_XLS
    workbook = xlrd.open_workbook(str(xls_path))
    sheet = workbook.sheet_by_index(0)
    rows = []
    for row_idx in range(1, sheet.nrows):
        price = sheet.cell_value(row_idx, 0)
        name_fa = str(sheet.cell_value(row_idx, 1)).strip()
        if name_fa:
            rows.append({
                'row': row_idx,
                'price': price,
                'name_fa': name_fa,
                'key': product_name_key(name_fa),
            })
    return rows


def get_english_name(name_fa: str, translations: dict | None = None) -> str | None:
    data = translations or load_translations()
    entry = data.get('products', {}).get(product_name_key(name_fa))
    if entry and entry.get('name_en'):
        return entry['name_en'].strip()
    return None


def upsert_translation(name_fa: str, name_en: str, price=None, translations: dict | None = None) -> dict:
    data = translations or load_translations()
    key = product_name_key(name_fa)
    data.setdefault('products', {})[key] = {
        'name_fa': name_fa,
        'name_en': name_en.strip(),
        'price': price,
        'key': key,
    }
    return data


def export_enriched_xlsx(
    translations: dict | None = None,
    output_path: Path | None = None,
    source_xls: Path | None = None,
):
    """ساخت اکسل سه‌ستونه: قیمت | نام فارسی | English Name"""
    data = translations or load_translations()
    products = data.get('products', {})
    rows = read_source_rows(source_xls)
    output_path = output_path or DEFAULT_ENRICHED_XLSX

    wb = Workbook()
    ws = wb.active
    ws.title = 'Products'
    ws.append(['مبلغ فروش', 'نام کالا', 'English Name'])

    for row in rows:
        entry = products.get(row['key'], {})
        name_en = entry.get('name_en', '')
        ws.append([row['price'], row['name_fa'], name_en])

    wb.save(output_path)
    return output_path


def build_search_queries_from_english(name_en: str) -> list[str]:
    """عبارت‌های جستجو بر اساس نام استاندارد انگلیسی."""
    name_en = ' '.join(name_en.split())
    if not name_en:
        return []

    queries = [
        f'"{name_en}" product',
        f'{name_en} product box',
        f'{name_en} pack',
        name_en,
    ]
    # حذف تکراری‌ها
    seen = set()
    unique = []
    for q in queries:
        q = q.strip()
        if q and q.lower() not in seen:
            seen.add(q.lower())
            unique.append(q)
    return unique[:5]
