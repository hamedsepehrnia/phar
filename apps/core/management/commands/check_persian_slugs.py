"""
دستور مدیریتی برای بررسی و تصحیح اسلاگ‌های فارسی
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.catalog.models import Product, Category, Brand


class Command(BaseCommand):
    help = 'بررسی و تصحیح اسلاگ‌های فارسی در محصولات، دسته‌بندی‌ها و برندها'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='تصحیح اسلاگ‌های مشکل‌دار'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='نمایش جزئیات بیشتر'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('شروع بررسی اسلاگ‌های فارسی...'))
        
        # بررسی محصولات
        self.check_products(options['fix'], options['verbose'])
        
        # بررسی دسته‌بندی‌ها
        self.check_categories(options['fix'], options['verbose'])
        
        # بررسی برندها
        self.check_brands(options['fix'], options['verbose'])
        
        self.stdout.write(self.style.SUCCESS('بررسی تکمیل شد.'))

    def check_products(self, fix=False, verbose=False):
        self.stdout.write('\n=== بررسی محصولات ===')
        
        products = Product.objects.all()
        problematic_count = 0
        fixed_count = 0
        
        for product in products:
            # ساخت اسلاگ جدید
            new_slug = slugify(product.name, allow_unicode=True)
            
            if product.slug != new_slug:
                problematic_count += 1
                
                if verbose:
                    self.stdout.write(
                        f'محصول: {product.name}\n'
                        f'اسلاگ فعلی: {product.slug}\n'
                        f'اسلاگ پیشنهادی: {new_slug}\n'
                        f'---'
                    )
                
                if fix:
                    try:
                        # بررسی تکراری نبودن
                        if not Product.objects.filter(slug=new_slug).exclude(id=product.id).exists():
                            product.slug = new_slug
                            product.save()
                            fixed_count += 1
                            if verbose:
                                self.stdout.write(self.style.SUCCESS(f'✅ اسلاگ محصول {product.name} اصلاح شد'))
                        else:
                            if verbose:
                                self.stdout.write(self.style.ERROR(f'❌ اسلاگ تکراری برای {product.name}'))
                    except Exception as e:
                        if verbose:
                            self.stdout.write(self.style.ERROR(f'❌ خطا در اصلاح {product.name}: {e}'))
        
        self.stdout.write(f'محصولات با مشکل: {problematic_count}')
        if fix:
            self.stdout.write(self.style.SUCCESS(f'محصولات اصلاح شده: {fixed_count}'))

    def check_categories(self, fix=False, verbose=False):
        self.stdout.write('\n=== بررسی دسته‌بندی‌ها ===')
        
        categories = Category.objects.all()
        problematic_count = 0
        fixed_count = 0
        
        for category in categories:
            new_slug = slugify(category.name, allow_unicode=True)
            
            if category.slug != new_slug:
                problematic_count += 1
                
                if verbose:
                    self.stdout.write(
                        f'دسته‌بندی: {category.name}\n'
                        f'اسلاگ فعلی: {category.slug}\n'
                        f'اسلاگ پیشنهادی: {new_slug}\n'
                        f'---'
                    )
                
                if fix:
                    try:
                        if not Category.objects.filter(slug=new_slug).exclude(id=category.id).exists():
                            category.slug = new_slug
                            category.save()
                            fixed_count += 1
                            if verbose:
                                self.stdout.write(self.style.SUCCESS(f'✅ اسلاگ دسته‌بندی {category.name} اصلاح شد'))
                        else:
                            if verbose:
                                self.stdout.write(self.style.ERROR(f'❌ اسلاگ تکراری برای {category.name}'))
                    except Exception as e:
                        if verbose:
                            self.stdout.write(self.style.ERROR(f'❌ خطا در اصلاح {category.name}: {e}'))
        
        self.stdout.write(f'دسته‌بندی‌های با مشکل: {problematic_count}')
        if fix:
            self.stdout.write(self.style.SUCCESS(f'دسته‌بندی‌های اصلاح شده: {fixed_count}'))

    def check_brands(self, fix=False, verbose=False):
        self.stdout.write('\n=== بررسی برندها ===')
        
        brands = Brand.objects.all()
        problematic_count = 0
        fixed_count = 0
        
        for brand in brands:
            new_slug = slugify(brand.name, allow_unicode=True)
            
            if brand.slug != new_slug:
                problematic_count += 1
                
                if verbose:
                    self.stdout.write(
                        f'برند: {brand.name}\n'
                        f'اسلاگ فعلی: {brand.slug}\n'
                        f'اسلاگ پیشنهادی: {new_slug}\n'
                        f'---'
                    )
                
                if fix:
                    try:
                        if not Brand.objects.filter(slug=new_slug).exclude(id=brand.id).exists():
                            brand.slug = new_slug
                            brand.save()
                            fixed_count += 1
                            if verbose:
                                self.stdout.write(self.style.SUCCESS(f'✅ اسلاگ برند {brand.name} اصلاح شد'))
                        else:
                            if verbose:
                                self.stdout.write(self.style.ERROR(f'❌ اسلاگ تکراری برای {brand.name}'))
                    except Exception as e:
                        if verbose:
                            self.stdout.write(self.style.ERROR(f'❌ خطا در اصلاح {brand.name}: {e}'))
        
        self.stdout.write(f'برندهای با مشکل: {problematic_count}')
        if fix:
            self.stdout.write(self.style.SUCCESS(f'برندهای اصلاح شده: {fixed_count}'))