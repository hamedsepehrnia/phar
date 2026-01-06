import json
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / 'ChatExport_2026-01-03' / 'result.json'
PHOTOS_DIR = ROOT / 'ChatExport_2026-01-03' / 'photos'
MEDIA_PRODUCTS = ROOT / 'media' / 'products'
FIXTURES_DIR = ROOT / 'apps' / 'catalog' / 'fixtures'
FIXTURE_FILE = FIXTURES_DIR / 'chat_import_products.json'

os.makedirs(MEDIA_PRODUCTS, exist_ok=True)
os.makedirs(FIXTURES_DIR, exist_ok=True)

def slugify(text):
    text = text.strip().lower()
    # Replace spaces with hyphens, remove unsafe chars
    text = re.sub(r"[\s]+", '-', text)
    text = re.sub(r"[^0-9a-z\-\u0600-\u06FF]", '', text)
    return text[:200]

with open(EXPORT, 'r', encoding='utf-8') as f:
    data = json.load(f)

messages = data.get('messages', [])
objects = []

# Create a default category and brand
category_pk = 100000
brand_pk = 100001
objects.append({
    'model': 'catalog.category',
    'pk': category_pk,
    'fields': {
        'name': 'Imported from chat',
        'slug': 'imported-from-chat',
        'parent': None,
        'description': 'Products imported from chat export',
        'is_active': True,
        'sort_order': 0,
        'meta_title': '',
        'meta_description': '',
        'created_at': None,
        'updated_at': None
    }
})

objects.append({
    'model': 'catalog.brand',
    'pk': brand_pk,
    'fields': {
        'name': 'Chat Import',
        'slug': 'chat-import',
        'logo': '',
        'description': 'Imported brand',
        'country': '',
        'is_active': True,
        'created_at': None
    }
})

prod_pk = 200000
img_pk = 300000
for m in messages:
    if m.get('type') != 'message':
        continue
    text = m.get('text') or ''
    if not text.strip() and not m.get('photo'):
        continue

    # derive name from first non-empty line
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    name = lines[0] if lines else f'Imported product {m.get("id")}'
    if len(name) > 250:
        name = name[:250]

    slug = slugify(name)
    if not slug:
        slug = f'product-{m.get("id")}'

    short_desc = (text.strip()[:497] + '...') if len(text.strip()) > 500 else text.strip()

    product_obj = {
        'model': 'catalog.product',
        'pk': prod_pk,
        'fields': {
            'name': name,
            'slug': slug + f'-{prod_pk}',
            'description': text,
            'short_description': short_desc,
            'category': category_pk,
            'brand': brand_pk,
            'price': 0,
            'compare_at_price': None,
            'sku': f'chat-{m.get("id")}',
            'stock_quantity': 10,
            'is_in_stock': True,
            'is_active': True,
            'prescription_required': False,
            'expiry_date': None,
            'batch_number': '',
            'max_purchase_per_user': 10,
            'meta_title': '',
            'meta_description': '',
            'view_count': 0,
            'sales_count': 0,
            'created_at': m.get('date'),
            'updated_at': m.get('date')
        }
    }
    objects.append(product_obj)

    # handle photo
    photo = m.get('photo')
    if photo:
        src = PHOTOS_DIR / Path(photo).name
        dst = MEDIA_PRODUCTS / Path(photo).name
        try:
            if src.exists():
                shutil.copy(str(src), str(dst))
                print(f'Copied {src} -> {dst}')
            else:
                print(f'Photo not found: {src}')
        except Exception as e:
            print('Error copying', src, e)

        image_obj = {
            'model': 'catalog.productimage',
            'pk': img_pk,
            'fields': {
                'product': prod_pk,
                'image': f'products/{Path(photo).name}',
                'alt_text': '',
                'is_main': True,
                'sort_order': 0,
                'created_at': m.get('date')
            }
        }
        objects.append(image_obj)
        img_pk += 1

    prod_pk += 1

# write fixture
with open(FIXTURE_FILE, 'w', encoding='utf-8') as f:
    json.dump(objects, f, ensure_ascii=False, indent=2)

print('Fixture written to', FIXTURE_FILE)
print('Copied photos to', MEDIA_PRODUCTS)
