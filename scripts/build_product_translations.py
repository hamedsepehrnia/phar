#!/usr/bin/env python3
"""Build product_translations.json and سایت-en.xlsx from batch translation dicts."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parent.parent
PRODUCTS_PATH = ROOT / 'data' / 'seed' / 'products_to_translate.json'
OUTPUT_JSON = ROOT / 'data' / 'seed' / 'product_translations.json'
OUTPUT_XLSX = ROOT / 'سایت-en.xlsx'
BATCH_FILES = [
    ROOT / 'scripts' / '_gen_translations_batch1.py',
    ROOT / 'scripts' / '_gen_translations_batch2.py',
    ROOT / 'scripts' / '_gen_translations_batch3.py',
    ROOT / 'scripts' / '_gen_translations_batch4.py',
]


def product_name_key(name: str) -> str:
    return hashlib.sha256(name.strip().encode('utf-8')).hexdigest()[:16]


def load_batch_translations(path: Path) -> dict:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.TRANSLATIONS


def main():
    products = json.loads(PRODUCTS_PATH.read_text(encoding='utf-8'))
    translations = {}
    for batch_path in BATCH_FILES:
        translations.update(load_batch_translations(batch_path))

    missing = []
    data = {'version': 1, 'products': {}}
    for item in products:
        name_fa = item['name_fa']
        name_en = translations.get(name_fa)
        if not name_en:
            missing.append(name_fa)
            continue
        key = product_name_key(name_fa)
        data['products'][key] = {
            'name_fa': name_fa,
            'name_en': name_en,
            'price': item['price'],
            'key': key,
        }

    if missing:
        print(f'Missing translations: {len(missing)}', file=sys.stderr)
        for name in missing[:20]:
            print(f'  - {name}', file=sys.stderr)
        sys.exit(1)

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )

    wb = Workbook()
    ws = wb.active
    ws.title = 'Products'
    ws.append(['مبلغ فروش', 'نام کالا', 'English Name'])
    for item in products:
        key = product_name_key(item['name_fa'])
        entry = data['products'][key]
        ws.append([item['price'], item['name_fa'], entry['name_en']])
    wb.save(OUTPUT_XLSX)

    print(f'Translations written: {len(data["products"])}')
    print(f'JSON: {OUTPUT_JSON}')
    print(f'Excel: {OUTPUT_XLSX}')


if __name__ == '__main__':
    main()
