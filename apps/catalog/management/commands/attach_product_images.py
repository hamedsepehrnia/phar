"""
اتصال تصاویر کش‌شده به محصولات موجود در دیتابیس

استفاده:
    python manage.py attach_product_images
    python manage.py attach_product_images --force
"""
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.catalog.models import Product
from apps.catalog.product_image_fetcher import (
    DEFAULT_MANIFEST_PATH,
    ProductImageFetcher,
    attach_image_to_product,
)
from apps.catalog.product_translations import product_name_key


class Command(BaseCommand):
    help = 'اتصال تصاویر data/seed/product_images/ به ProductImage در دیتابیس'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='جایگزینی تصویر حتی اگر محصول از قبل عکس داشته باشد',
        )

    def handle(self, *args, **options):
        fetcher = ProductImageFetcher()
        products = Product.objects.all().order_by('id')

        attached = skipped = missing = no_image = 0

        for product in products:
            entry = fetcher.get_cached_entry(product.name)

            if not entry or entry.get('status') != 'ok':
                no_image += 1
                continue

            image_file = entry.get('image_file')
            if not image_file or not Path(image_file).exists():
                missing += 1
                continue

            if product.images.exists() and not options['force']:
                skipped += 1
                continue

            if attach_image_to_product(product, image_file, product.name):
                attached += 1
            else:
                missing += 1

        self.stdout.write(self.style.SUCCESS(
            f'متصل شد: {attached} | از قبل داشت: {skipped} | '
            f'بدون کش: {no_image} | فایل ناموجود: {missing}\n'
            f'Manifest: {DEFAULT_MANIFEST_PATH}'
        ))
