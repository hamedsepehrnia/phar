import os
import random
import shutil
from decimal import Decimal

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from faker import Faker

from apps.catalog.models import Brand, Category, Product, ProductImage
from apps.core.models import Banner, Slider


class Command(BaseCommand):
    help = "پاک‌سازی داده‌های نمونه و تولید داده‌ی جدید با تصاویر معتبر"

    def add_arguments(self, parser):
        parser.add_argument(
            "--products",
            type=int,
            default=24,
            help="تعداد محصولاتی که ساخته می‌شود (پیش‌فرض 24)",
        )

    def handle(self, *args, **options):
        product_count = options["products"]
        faker = Faker("fa_IR")

        with transaction.atomic():
            self._clear_media()
            self._clear_data()

            leaf_categories = self._create_categories()
            brands = self._create_brands()
            self._create_sliders()
            self._create_banners()
            self._create_products(faker, leaf_categories, brands, product_count)

        self.stdout.write(self.style.SUCCESS("داده‌های نمونه با تصاویر معتبر با موفقیت ایجاد شد."))

    # ---------------------- helpers ----------------------
    def _static_path(self, rel_path: str) -> str:
        full_path = os.path.join(settings.BASE_DIR, "static", rel_path)
        if not os.path.exists(full_path):
            raise CommandError(f"فایل استاتیک یافت نشد: {rel_path}")
        return full_path

    def _assign_image(self, instance, field_name: str, rel_path: str, filename: str):
        full_path = self._static_path(rel_path)
        with open(full_path, "rb") as f:
            getattr(instance, field_name).save(filename, File(f), save=True)

    def _clear_media(self):
        media_dirs = [
            "products",
            "categories",
            "brands",
            "sliders",
            "banners",
        ]
        for folder in media_dirs:
            path = os.path.join(settings.MEDIA_ROOT, folder)
            if os.path.exists(path):
                shutil.rmtree(path)

    def _clear_data(self):
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()
        Slider.objects.all().delete()
        Banner.objects.all().delete()

    def _unique_slug(self, model, base: str) -> str:
        slug = slugify(base, allow_unicode=True)
        while model.objects.filter(slug=slug).exists():
            slug = f"{slug}-{random.randint(100,999)}"
        return slug

    def _create_category_node(self, name, img_rel, parent, sort_order):
        cat = Category(
            name=name,
            slug=self._unique_slug(Category, name),
            description=f"دسته {name}",
            sort_order=sort_order,
            is_active=True,
            parent=parent,
        )
        cat.save()
        self._assign_image(cat, "image", img_rel, f"{cat.slug}.jpg")
        return cat

    def _create_categories(self):
        # سه لایه (دسته ← زیردسته ← زیرِ زیردسته)
        tree = [
            (
                "مراقبت پوست",
                "images/product/01.jpg",
                [
                    ("پاک‌کننده و تونر", "images/product/02.jpg", [
                        ("میسلار واتر", "images/product/03.jpg", []),
                        ("فوم و ژل شستشو", "images/product/04.jpg", []),
                    ]),
                    ("مرطوب‌کننده و سرم", "images/product/05.jpg", [
                        ("سرم ویتامین C", "images/product/06.jpg", []),
                        ("کرم دور چشم", "images/product/01.jpg", []),
                    ]),
                ],
            ),
            (
                "مراقبت مو",
                "images/product/02.jpg",
                [
                    ("شامپو و شستشو", "images/product/03.jpg", [
                        ("شامپو تقویتی", "images/product/04.jpg", []),
                        ("شامپو ضدریزش", "images/product/05.jpg", []),
                    ]),
                    ("نرم‌کننده و ماسک", "images/product/06.jpg", [
                        ("ماسک مو", "images/product/01.jpg", []),
                        ("نرم‌کننده مغذی", "images/product/02.jpg", []),
                    ]),
                ],
            ),
            (
                "آرایشی",
                "images/product/03.jpg",
                [
                    ("پوست", "images/product/04.jpg", [
                        ("کرم پودر", "images/product/05.jpg", []),
                        ("پرایمر و بیس", "images/product/06.jpg", []),
                    ]),
                    ("لب و چشم", "images/product/01.jpg", [
                        ("رژ لب", "images/product/02.jpg", []),
                        ("ریمل و خط چشم", "images/product/03.jpg", []),
                    ]),
                ],
            ),
            (
                "بهداشت شخصی",
                "images/product/04.jpg",
                [
                    ("بدن", "images/product/05.jpg", [
                        ("ضدعفونی و بهداشت", "images/product/06.jpg", []),
                        ("دئودورانت", "images/product/01.jpg", []),
                    ]),
                    ("دهان و دندان", "images/product/02.jpg", [
                        ("مسواک و خمیردندان", "images/product/03.jpg", []),
                        ("دهان‌شویه", "images/product/04.jpg", []),
                    ]),
                ],
            ),
            (
                "مکمل ها",
                "images/product/05.jpg",
                [
                    ("ویتامین ها", "images/product/06.jpg", [
                        ("مولتی ویتامین", "images/product/01.jpg", []),
                        ("ویتامین C", "images/product/02.jpg", []),
                    ]),
                    ("ورزشی", "images/product/03.jpg", [
                        ("پروتئین", "images/product/04.jpg", []),
                        ("کراتین", "images/product/05.jpg", []),
                    ]),
                ],
            ),
        ]

        all_nodes = []
        leaf_nodes = []

        def build(nodes, parent=None):
            for name, img, children in nodes:
                sort_order = len(all_nodes)
                node = self._create_category_node(name, img, parent, sort_order)
                all_nodes.append(node)
                if children:
                    build(children, node)
                else:
                    leaf_nodes.append(node)

        build(tree)
        return leaf_nodes

    def _create_brands(self):
        names = [
            "گلناز لَب",
            "رویال اسکین",
            "نچرال کِر",
            "درماتیک",
            "پیور وی",
            "اورگنیک پلاس",
        ]
        brand_logo = "images/logo.svg"
        brands = []
        for name in names:
            brand = Brand(
                name=name,
                slug=self._unique_slug(Brand, name),
                country="ایران",
                description=f"برند {name}",
                is_active=True,
            )
            brand.save()
            # اگر لوگو موجود نبود، ارور می‌دهد تا زود متوجه شویم
            self._assign_image(brand, "logo", brand_logo, f"{brand.slug}.svg")
            brands.append(brand)
        return brands

    def _create_sliders(self):
        slider_images = [
            "images/slider/01.jpg",
            "images/slider/02.jpg",
            "images/slider/03.jpg",
        ]
        for idx, rel in enumerate(slider_images, start=1):
            slider = Slider(
                title=f"اسلاید {idx}",
                subtitle="پیشنهاد ویژه محصولات زیبایی",
                link="/shop/",
                sort_order=idx,
                is_active=True,
            )
            slider.save()
            self._assign_image(slider, "image", rel, f"slider-{idx}.jpg")

    def _create_banners(self):
        banner_sets = [
            ("بنر بالای صفحه", "home_top", "images/banners/banner-grid/01.jpg"),
            ("بنر میانی", "home_middle", "images/banners/banner-grid/02.jpg"),
            ("بنر پایینی", "home_bottom", "images/banners/banner-grid/03.jpg"),
            ("بنر فروشگاه", "shop_top", "images/banners/banner-grid/04.jpg"),
        ]
        for idx, (title, pos, rel) in enumerate(banner_sets, start=1):
            banner = Banner(
                title=title,
                position=pos,
                link="/shop/",
                sort_order=idx,
                is_active=True,
            )
            banner.save()
            self._assign_image(banner, "image", rel, f"banner-{idx}.jpg")

    def _create_products(self, faker, categories, brands, count):
        product_images_pool = [
            "images/product/01.jpg",
            "images/product/02.jpg",
            "images/product/03.jpg",
            "images/product/04.jpg",
            "images/product/05.jpg",
            "images/product/06.jpg",
        ]
        adjectives = ["مرطوب‌کننده", "بازسازی", "ضدآکنه", "محافظ", "پایه آرایش", "تقویتی", "ویتامینه"]
        types = ["کرم", "سرم", "تونر", "ماسک", "شامپو", "روغن", "کاندیشنر", "کرم پودر", "رژ لب", "ضدآفتاب"]

        for i in range(count):
            name = f"{random.choice(types)} {random.choice(adjectives)} {faker.word()}"
            slug = self._unique_slug(Product, name)
            category = random.choice(categories)
            brand = random.choice(brands)

            price = Decimal(random.randint(180_000, 1_100_000))
            compare = price + Decimal(random.randint(30_000, 250_000)) if random.random() < 0.65 else None

            product = Product(
                name=name,
                slug=slug,
                description=faker.paragraph(nb_sentences=3),
                short_description=faker.sentence(nb_words=10),
                category=category,
                brand=brand,
                price=price,
                compare_at_price=compare,
                sku=f"SKU-{random.randint(100000,999999)}",
                stock_quantity=random.randint(6, 60),
                prescription_required=random.random() < 0.1,
                max_purchase_per_user=10,
                is_active=True,
            )
            product.save()

            chosen_images = random.sample(product_images_pool, k=2)
            for idx, rel in enumerate(chosen_images):
                full_path = self._static_path(rel)
                ext = os.path.splitext(rel)[1] or ".jpg"
                with open(full_path, "rb") as f:
                    ProductImage.objects.create(
                        product=product,
                        image=File(f, name=f"{slug}-{idx+1}{ext}"),
                        alt_text=name,
                        is_main=(idx == 0),
                        sort_order=idx,
                    )

            # بروزرسانی وضعیت موجودی بر اساس stock_quantity
            product.is_in_stock = product.stock_quantity > 0
            product.save()

            self.stdout.write(f"محصول ایجاد شد: {name}")
