import random
import string
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.catalog.models import Product, Category, Brand


def unique_slug(base_slug):
    slug = base_slug
    while Product.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{random.randint(1000, 9999)}"
    return slug


def unique_sku(prefix="SKU"):
    while True:
        code = f"{prefix}-{random.randint(100000, 999999)}"
        if not Product.objects.filter(sku=code).exists():
            return code


class Command(BaseCommand):
    help = "Generate random products without images for testing"

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100, help='How many products to create (default: 100)')

    def handle(self, *args, **options):
        count = max(1, options['count'])

        categories = list(Category.objects.filter(is_active=True))
        if not categories:
            default_cat, _ = Category.objects.get_or_create(
                name='محصولات عمومی',
                defaults={'slug': slugify('محصولات عمومی', allow_unicode=True)}
            )
            categories = [default_cat]

        brands = list(Brand.objects.filter(is_active=True))

        adjectives = ['پلاس', 'اکسترا', 'ویژه', 'سریع', 'ملایم', 'حرفه‌ای', 'پایه', 'پیشرفته']
        nouns = ['کپسول', 'شربت', 'قرص', 'کرم', 'ژل', 'محلول', 'پودر', 'ویتامین']

        created = 0
        for idx in range(count):
            name = f"{random.choice(nouns)} {random.choice(adjectives)} {random.randint(100, 999)}"
            base_slug = slugify(name, allow_unicode=True)
            slug = unique_slug(base_slug)
            sku = unique_sku(prefix='RND')

            category = random.choice(categories)
            brand = random.choice(brands) if brands and random.random() > 0.35 else None

            price_value = random.randrange(50000, 900000, 5000)
            compare_price = None
            if random.random() > 0.5:
                compare_price = int(price_value * random.uniform(1.1, 1.4))

            stock_qty = random.randint(0, 80)

            product_data = {
                'name': name,
                'slug': slug,
                'description': f"این یک محصول تستی با نام {name} است.",
                'short_description': f"نمونه آزمایشی {name}",
                'category': category,
                'brand': brand,
                'price': Decimal(price_value),
                'compare_at_price': Decimal(compare_price) if compare_price else None,
                'sku': sku,
                'stock_quantity': stock_qty,
                'is_in_stock': stock_qty > 0,
                'is_active': True,
                'prescription_required': False,
            }

            with transaction.atomic():
                Product.objects.create(**product_data)
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} random products."))
