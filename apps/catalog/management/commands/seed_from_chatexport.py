import json
import os
import re
from decimal import Decimal

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from django.conf import settings

from apps.catalog.models import Category, Product, ProductImage, Brand


KEYWORD_CATEGORY_MAP = {
    'کلاژن': 'مکمل های پوست و زیبایی',
    'هیالورون': 'مکمل های پوست و زیبایی',
    'گلوتاتیون': 'مکمل های پوست و زیبایی',
    'بیوتین': 'مکمل های مو و ناخن',
    'بیوتی': 'مکمل های مو و ناخن',
    'زینک': 'مکمل های مو و ناخن',
    'ب کمپلکس': 'ویتامین‌ها و مکمل‌ها',
    'ویتامین': 'ویتامین‌ها و مکمل‌ها',
    'کاهش وزن': 'مکمل های لاغری',
    'بایونا': 'مکمل های گیاهی',
    'پروتئین': 'پروتئین و مکمل های ورزشی',
}


def assign_category(name, text):
    combined = (name or '') + ' ' + (text or '')
    for kw, cat in KEYWORD_CATEGORY_MAP.items():
        if kw in combined:
            return cat
    return 'سایر مکمل‌ها'


def extract_name(text):
    if not text:
        return None
    text = text.strip()
    # use the first non-empty line
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), '')
    if not first_line:
        # fallback: take first 6 words
        return ' '.join(text.split()[:6])

    # split on repeated spaces to try separate name from description
    parts = re.split(r'\s{2,}| - | – |—', first_line)
    name = parts[0].strip()
    # If name is very short (e.g., single short word), try extend to two words
    if len(name) < 3 and len(parts) > 1:
        name = parts[0] + ' ' + parts[1]
    return name


class Command(BaseCommand):
    help = 'Create categories and products from chat export JSON (ChatExport_*/result.json)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json', '-j',
            default=os.path.join(settings.BASE_DIR, 'ChatExport_2026-01-03', 'result.json'),
            help='Path to exported JSON file'
        )
        parser.add_argument(
            '--photos-dir', '-p',
            default=os.path.join(settings.BASE_DIR, 'ChatExport_2026-01-03'),
            help='Base dir for photo paths in JSON (defaults to ChatExport_2026-01-03)'
        )
        parser.add_argument('--dry-run', action='store_true', help='Parse and show summary without creating records')

    def handle(self, *args, **options):
        json_path = options['json']
        photos_base = options['photos_dir']
        dry_run = options['dry_run']

        if not os.path.exists(json_path):
            self.stderr.write(self.style.ERROR(f'JSON file not found: {json_path}'))
            return

        with open(json_path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)

        messages = data.get('messages', [])
        created = 0
        skipped = 0
        images_attached = 0

        # cache of created categories to avoid repeated DB hits
        category_cache = {}

        for msg in messages:
            # we focus on messages that have text or photo
            text = msg.get('text') or ''
            name = extract_name(text)
            photo = msg.get('photo')

            if not name:
                skipped += 1
                continue

            cat_name = assign_category(name, text)
            if cat_name in category_cache:
                category = category_cache[cat_name]
            else:
                category, _ = Category.objects.get_or_create(name=cat_name, defaults={'slug': slugify(cat_name, allow_unicode=True)})
                category_cache[cat_name] = category

            sku = f'chat-{msg.get("id")}'

            # Build product data - fields that are not available will be optional/defaulted
            product_data = {
                'name': name,
                'description': text or '',
                'short_description': (text or '')[:500],
                'category': category,
                'brand': None,
                'price': Decimal('0'),
                'compare_at_price': None,
                'sku': sku,
                'stock_quantity': 0,
                'is_active': True,
                'prescription_required': False,
            }

            # ensure unique slug — append id to avoid slug collisions
            base_slug = slugify(name, allow_unicode=True)
            slug = base_slug
            if Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{msg.get('id')}"
                product_data['slug'] = slug

            if dry_run:
                self.stdout.write(f"[DRY] Would create product: {product_data['name']} (category={cat_name}, sku={sku})")
                created += 1
                continue

            try:
                with transaction.atomic():
                    product = Product.objects.create(**product_data)
                    created += 1

                    # attach photo if exists
                    if photo:
                        photo_path = os.path.join(photos_base, photo)
                        if os.path.exists(photo_path):
                            try:
                                with open(photo_path, 'rb') as pf:
                                    fname = os.path.basename(photo_path)
                                    pi = ProductImage(product=product, alt_text=product.name, is_main=True)
                                    pi.image.save(fname, File(pf), save=True)
                                    images_attached += 1
                            except Exception as e:
                                self.stderr.write(self.style.WARNING(f'Failed to attach image {photo_path} -> {e}'))
                        else:
                            self.stderr.write(self.style.WARNING(f'Photo file not found: {photo_path}'))

            except Exception as exc:
                skipped += 1
                self.stderr.write(self.style.ERROR(f'Failed to create product for message {msg.get("id")}: {exc}'))

        self.stdout.write(self.style.SUCCESS(f'Done. Created products: {created}, images attached: {images_attached}, skipped: {skipped}'))
