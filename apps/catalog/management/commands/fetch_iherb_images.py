"""Deprecated wrapper — use fetch_product_images."""
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Deprecated — use: python manage.py fetch_product_images'

    def add_arguments(self, parser):
        parser.add_argument('--from-db', action='store_true')
        parser.add_argument('--file', '-f', default='')
        parser.add_argument('--limit', type=int, default=0)
        parser.add_argument('--force', action='store_true')
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING(
            'fetch_iherb_images منسوخ شد → fetch_product_images'
        ))
        kwargs = {k: v for k, v in options.items() if v or k in ('from_db', 'force', 'dry_run')}
        call_command('fetch_product_images', **kwargs)
