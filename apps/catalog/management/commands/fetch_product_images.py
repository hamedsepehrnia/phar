"""
دانلود تصویر واقعی محصول — crawler با queue و throttling

پیش‌نیاز:
    python manage.py translate_site_products

استفاده:
    python manage.py fetch_product_images
    python manage.py fetch_product_images --limit 20 --batch-size 10 --batch-pause 90
    python manage.py fetch_product_images --enable-ddg   # اختیاری، آخرین fallback
"""
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.catalog.image_crawler.rate_limit import CrawlRateLimiter
from apps.catalog.product_image_fetcher import DEFAULT_MANIFEST_PATH, ProductImageFetcher
from apps.catalog.product_translations import (
    DEFAULT_TRANSLATIONS_PATH,
    get_english_name,
    load_translations,
    read_source_rows,
)
from apps.catalog.models import Product


class Command(BaseCommand):
    help = 'Crawler تصویر محصول — Torob → iHerb → Digikala → (اختیاری) DDG'

    def add_arguments(self, parser):
        parser.add_argument('--from-db', action='store_true')
        parser.add_argument(
            '--file', '-f',
            default=str(Path(settings.BASE_DIR) / 'سایت.Xls'),
        )
        parser.add_argument('--limit', type=int, default=0)
        parser.add_argument('--force', action='store_true')
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--enable-ddg', action='store_true', help='DDG فقط fallback (rate-limit prone)')
        parser.add_argument('--batch-size', type=int, default=15, help='توقف بین batchها')
        parser.add_argument('--batch-pause', type=float, default=60.0, help='ثانیه استراحت بین batch')
        parser.add_argument('--min-delay', type=float, default=2.0)
        parser.add_argument('--max-delay', type=float, default=5.0)

    def handle(self, *args, **options):
        translations = load_translations()
        if not translations.get('products'):
            raise CommandError(
                f'ابتدا: python manage.py translate_site_products\n'
                f'({DEFAULT_TRANSLATIONS_PATH})'
            )

        items = self._load_items(options, translations)
        if options['limit']:
            items = items[: options['limit']]

        self.stdout.write(
            f'محصولات: {len(items)} | batch={options["batch_size"]} | '
            f'pause={options["batch_pause"]}s | delay={options["min_delay"]}-{options["max_delay"]}s'
        )

        if options['dry_run']:
            for item in items[:10]:
                self.stdout.write(f'{item["name_fa"][:45]} → {item["name_en"]}')
            return

        limiter = CrawlRateLimiter(
            min_delay=options['min_delay'],
            max_delay=options['max_delay'],
            batch_size=options['batch_size'],
            batch_pause=options['batch_pause'],
        )

        ok = fail = skip = no_tr = 0

        with ProductImageFetcher(
            enable_ddg=options['enable_ddg'],
            limiter=limiter,
        ) as fetcher:
            for idx, item in enumerate(items, start=1):
                name_fa, name_en = item['name_fa'], item['name_en']
                if not name_en:
                    no_tr += 1
                    continue

                cached = fetcher.get_cached_entry(name_fa)
                if cached and cached.get('status') == 'ok' and not options['force']:
                    skip += 1
                    if idx % 25 == 0:
                        self.stdout.write(f'[{idx}/{len(items)}] … (cached)')
                    continue

                result = fetcher.fetch_product_image(
                    name_fa,
                    name_en=name_en,
                    force=options['force'],
                    item_index=idx,
                )
                if result['status'] == 'ok':
                    ok += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'[{idx}/{len(items)}] ✓ {result["source"]} | '
                        f'{name_fa[:35]} | score={result.get("match_score", 0):.2f}'
                    ))
                else:
                    fail += 1
                    self.stdout.write(self.style.WARNING(
                        f'[{idx}/{len(items)}] ✗ {result["status"]} | {name_fa[:40]}'
                    ))

        self.stdout.write(self.style.SUCCESS(
            f'\nموفق: {ok} | ناموفق: {fail} | کش: {skip} | بدون ترجمه: {no_tr}\n'
            f'Manifest: {DEFAULT_MANIFEST_PATH}'
        ))

    def _load_items(self, options, translations) -> list[dict]:
        if options['from_db']:
            return [{
                'name_fa': n,
                'name_en': get_english_name(n, translations) or '',
            } for n in Product.objects.order_by('id').values_list('name', flat=True)]

        return [{
            'name_fa': r['name_fa'],
            'name_en': get_english_name(r['name_fa'], translations) or '',
        } for r in read_source_rows(Path(options['file']))]
