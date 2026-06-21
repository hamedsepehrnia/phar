"""
ترجمه AI نام محصولات فارسی → انگلیسی و ساخت اکسل enriched

استفاده:
    # ابتدا OPENAI_API_KEY را در .env تنظیم کنید
    python manage.py translate_site_products
    python manage.py translate_site_products --limit 50
    python manage.py translate_site_products --batch-size 25
"""
import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.catalog.ai_translator import is_configured, translate_batch
from apps.catalog.product_translations import (
    DEFAULT_ENRICHED_XLSX,
    DEFAULT_SOURCE_XLS,
    DEFAULT_TRANSLATIONS_PATH,
    export_enriched_xlsx,
    load_translations,
    read_source_rows,
    save_translations,
    upsert_translation,
)


class Command(BaseCommand):
    help = 'ترجمه AI نام محصولات و ساخت ستون English Name در اکسل'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file', '-f',
            default=str(DEFAULT_SOURCE_XLS),
            help='فایل اکسل منبع',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=25,
            help='تعداد محصول در هر درخواست AI (پیش‌فرض ۲۵)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='محدود کردن تعداد (۰ = همه)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='ترجمه مجدد حتی اگر موجود باشد',
        )

    def handle(self, *args, **options):
        if not is_configured():
            raise CommandError(
                'OPENAI_API_KEY در .env تنظیم نشده.\n'
                'مثال:\nOPENAI_API_KEY=sk-...\n'
                'OPENAI_MODEL=gpt-4o-mini  # اختیاری'
            )

        source = Path(options['file'])
        if not source.exists():
            raise CommandError(f'فایل یافت نشد: {source}')

        rows = read_source_rows(source)
        if options['limit']:
            rows = rows[: options['limit']]

        data = load_translations()
        batch_size = options['batch_size']
        translated = 0
        skipped = 0

        pending = []
        for row in rows:
            existing = data.get('products', {}).get(row['key'])
            if existing and existing.get('name_en') and not options['force']:
                skipped += 1
                continue
            pending.append(row)

        self.stdout.write(
            f'کل: {len(rows)} | نیاز به ترجمه: {len(pending)} | از کش: {skipped}'
        )

        for i in range(0, len(pending), batch_size):
            batch_rows = pending[i:i + batch_size]
            names = [r['name_fa'] for r in batch_rows]
            self.stdout.write(f'ترجمه دسته {i // batch_size + 1} ({len(names)} محصول)...')

            mapping = translate_batch(names)
            if not mapping:
                self.stderr.write(self.style.ERROR(f'دسته {i // batch_size + 1} ناموفق بود'))
                continue

            for row in batch_rows:
                name_en = mapping.get(row['name_fa'])
                if name_en:
                    data = upsert_translation(
                        row['name_fa'], name_en, row['price'], data,
                    )
                    translated += 1
                    self.stdout.write(f'  ✓ {row["name_fa"][:45]} → {name_en}')
                else:
                    self.stderr.write(self.style.WARNING(
                        f'  ✗ بدون ترجمه: {row["name_fa"][:50]}'
                    ))

            save_translations(data)
            time.sleep(1)

        xlsx_path = export_enriched_xlsx(data)
        save_translations(data)

        self.stdout.write(self.style.SUCCESS(
            f'\nترجمه انجام شد: {translated} محصول\n'
            f'JSON: {DEFAULT_TRANSLATIONS_PATH}\n'
            f'Excel: {xlsx_path}'
        ))
