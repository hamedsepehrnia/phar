"""
سید اولیه محصولات از فایل سایت.Xls

گردش کار پیشنهادی:
    1. python manage.py translate_site_products   # ترجمه AI → سایت-en.xlsx
    2. python manage.py fetch_product_images      # دانلود عکس واقعی
    3. python manage.py seed_site_products --with-images
"""
import os
from decimal import Decimal, InvalidOperation
from pathlib import Path

import xlrd
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.catalog.category_classifier import CATEGORY_TREE, classify_product
from apps.catalog.models import (
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductImage,
    Wishlist,
)
from apps.core.models import Banner, Slider


DEFAULT_STOCK = 10


def parse_price(raw_value) -> Decimal:
    """تبدیل مبلغ فروش از اکسل به Decimal (تومان)."""
    if raw_value is None or raw_value == '':
        return Decimal('0')

    if isinstance(raw_value, (int, float)):
        return Decimal(str(int(raw_value)))

    text = str(raw_value).strip().replace(',', '').replace('،', '')
    if not text:
        return Decimal('0')

    try:
        return Decimal(str(int(float(text))))
    except (ValueError, InvalidOperation):
        return Decimal('0')


def unique_slug(model, base: str, used_slugs: set | None = None) -> str:
    slug = slugify(base, allow_unicode=True) or 'product'
    candidate = slug
    counter = 2
    used = used_slugs or set()

    while candidate in used or model.objects.filter(slug=candidate).exists():
        candidate = f'{slug}-{counter}'
        counter += 1

    used.add(candidate)
    return candidate


class Command(BaseCommand):
    help = 'پاک‌سازی کاتالوگ و بارگذاری محصولات از فایل سایت.Xls'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file', '-f',
            default=os.path.join(settings.BASE_DIR, 'سایت.Xls'),
            help='مسیر فایل اکسل محصولات (پیش‌فرض: سایت.Xls در ریشه پروژه)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='فقط گزارش بده، چیزی در دیتابیس ذخیره نشود',
        )
        parser.add_argument(
            '--no-clear',
            action='store_true',
            help='داده‌های قبلی کاتالوگ پاک نشود (فقط برای بروزرسانی)',
        )
        parser.add_argument(
            '--stock',
            type=int,
            default=DEFAULT_STOCK,
            help=f'موجودی پیش‌فرض هر محصول (پیش‌فرض: {DEFAULT_STOCK})',
        )
        parser.add_argument(
            '--with-images',
            action='store_true',
            help='اتصال تصاویر واقعی از کش (data/seed/product_images/)',
        )
        parser.add_argument(
            '--fetch-images',
            action='store_true',
            help='قبل از سید، تصاویر ناقص را با fetch_product_images دانلود کن',
        )

    def handle(self, *args, **options):
        xls_path = options['file']
        dry_run = options['dry_run']
        clear_data = not options['no_clear']
        stock_qty = options['stock']
        with_images = options['with_images']
        fetch_images = options['fetch_images']

        if not os.path.exists(xls_path):
            raise CommandError(f'فایل یافت نشد: {xls_path}')

        rows = self._read_excel(xls_path)
        if not rows:
            raise CommandError('هیچ محصولی در فایل یافت نشد.')

        if fetch_images and not dry_run:
            self._fetch_missing_images(rows)

        if with_images and not dry_run:
            self._validate_image_cache(rows)

        self.stdout.write(f'تعداد محصولات در فایل: {len(rows)}')

        if dry_run:
            self._dry_run_report(rows, stock_qty)
            return

        with transaction.atomic():
            if clear_data:
                self._clear_catalog()
                self.stdout.write(self.style.WARNING('داده‌های قبلی کاتالوگ پاک شد.'))

            category_map = self._create_categories()
            created, skipped = self._create_products(
                rows, category_map, stock_qty, attach_images=with_images,
            )

        self.stdout.write(self.style.SUCCESS(
            f'سید با موفقیت انجام شد. '
            f'دسته‌بندی: {len(category_map)}, '
            f'محصول ایجاد شده: {created}, '
            f'رد شده: {skipped}'
        ))

    def _read_excel(self, path: str) -> list[tuple[Decimal, str]]:
        workbook = xlrd.open_workbook(path)
        sheet = workbook.sheet_by_index(0)
        rows = []

        for row_idx in range(1, sheet.nrows):
            price = parse_price(sheet.cell_value(row_idx, 0))
            name = str(sheet.cell_value(row_idx, 1)).strip()
            if name:
                rows.append((price, name))

        return rows

    def _dry_run_report(self, rows, stock_qty):
        from collections import Counter

        counts = Counter()
        for _, name in rows:
            parent, leaf = classify_product(name)
            counts[(parent, leaf)] += 1

        self.stdout.write(self.style.NOTICE('=== حالت dry-run ==='))
        self.stdout.write(f'موجودی پیش‌فرض: {stock_qty}')
        self.stdout.write('\nتوزیع دسته‌بندی:')
        for (parent, leaf), count in sorted(counts.items(), key=lambda x: -x[1]):
            self.stdout.write(f'  {parent} > {leaf}: {count}')

        self.stdout.write('\nنمونه ۵ محصول اول:')
        for price, name in rows[:5]:
            parent, leaf = classify_product(name)
            self.stdout.write(
                f'  [{parent} > {leaf}] {name} — {price:,} تومان — موجودی: {stock_qty}'
            )

    def _clear_catalog(self):
        """پاک‌سازی کامل داده‌های کاتالوگ و محتوای نمایشی."""
        Wishlist.objects.all().delete()
        ProductAttributeValue.objects.all().delete()
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()
        ProductAttribute.objects.all().delete()
        Slider.objects.all().delete()
        Banner.objects.all().delete()

    def _create_categories(self) -> dict[tuple[str, str], Category]:
        """ساخت درخت دسته‌بندی و برگرداندن نقشه (والد, برگ) → Category."""
        cache: dict[tuple[str, str], Category] = {}
        sort_order = 0

        for parent_name, children in CATEGORY_TREE.items():
            parent = Category.objects.create(
                name=parent_name,
                slug=unique_slug(Category, parent_name),
                sort_order=sort_order,
                is_active=True,
            )
            sort_order += 1

            for child_idx, child_name in enumerate(children):
                child = Category.objects.create(
                    name=child_name,
                    slug=unique_slug(Category, f'{parent_name}-{child_name}'),
                    parent=parent,
                    sort_order=child_idx,
                    is_active=True,
                )
                cache[(parent_name, child_name)] = child

        return cache

    def _create_products(
        self,
        rows: list[tuple[Decimal, str]],
        category_map: dict[tuple[str, str], Category],
        stock_qty: int,
        attach_images: bool = False,
    ) -> tuple[int, int]:
        from apps.catalog.product_image_fetcher import ProductImageFetcher, attach_image_to_product
        from apps.catalog.product_translations import get_english_name

        fetcher = ProductImageFetcher()
        created = 0
        skipped = 0
        images_attached = 0
        used_slugs: set[str] = set()

        for index, (price, name) in enumerate(rows, start=1):
            parent_name, leaf_name = classify_product(name)
            category = category_map.get((parent_name, leaf_name))

            if not category:
                category = category_map.get(('سایر محصولات', 'متفرقه'))
                self.stderr.write(self.style.WARNING(
                    f'دسته نامشخص برای «{name}» — در متفرقه قرار گرفت.'
                ))

            slug = unique_slug(Product, name, used_slugs)

            try:
                product = Product.objects.create(
                    name=name,
                    slug=slug,
                    description='',
                    short_description='',
                    category=category,
                    brand=None,
                    price=price,
                    compare_at_price=None,
                    sku=None,
                    stock_quantity=stock_qty,
                    is_in_stock=True,
                    is_active=True,
                    prescription_required=False,
                    expiry_date=None,
                    batch_number='',
                    max_purchase_per_user=10,
                    meta_title='',
                    meta_description='',
                )
                created += 1

                if attach_images:
                    entry = fetcher.get_cached_entry(name)
                    if entry and entry.get('status') == 'ok' and entry.get('image_file'):
                        if attach_image_to_product(product, entry['image_file'], name):
                            images_attached += 1

            except Exception as exc:
                skipped += 1
                self.stderr.write(self.style.ERROR(
                    f'خطا در ایجاد «{name}»: {exc}'
                ))

        if attach_images:
            self.stdout.write(f'تصاویر متصل شده: {images_attached}/{created}')

        return created, skipped

    def _fetch_missing_images(self, rows):
        from apps.catalog.product_image_fetcher import ProductImageFetcher
        from apps.catalog.product_translations import get_english_name, load_translations

        translations = load_translations()
        if not translations.get('products'):
            raise CommandError(
                'ابتدا: python manage.py translate_site_products'
            )

        self.stdout.write('در حال دانلود تصاویر واقعی محصول...')
        with ProductImageFetcher() as fetcher:
            for idx, (_, name) in enumerate(rows, start=1):
                name_en = get_english_name(name, translations)
                if not name_en:
                    continue
                cached = fetcher.get_cached_entry(name)
                if cached and cached.get('status') == 'ok':
                    continue
                result = fetcher.fetch_product_image(name, name_en=name_en)
                if result.get('status') == 'ok' and idx % 10 == 0:
                    self.stdout.write(f'  [{idx}/{len(rows)}] ✓')

    def _validate_image_cache(self, rows):
        from apps.catalog.product_image_fetcher import DEFAULT_MANIFEST_PATH, ProductImageFetcher

        fetcher = ProductImageFetcher()
        missing = []
        for _, name in rows:
            entry = fetcher.get_cached_entry(name)
            if not entry or entry.get('status') != 'ok':
                missing.append(name)

        if missing:
            self.stdout.write(self.style.WARNING(
                f'{len(missing)} محصول بدون تصویر واقعی.\n'
                f'  python manage.py translate_site_products\n'
                f'  python manage.py fetch_product_images\n'
                f'Manifest: {DEFAULT_MANIFEST_PATH}'
            ))
