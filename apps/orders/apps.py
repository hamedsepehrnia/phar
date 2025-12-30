from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'
    verbose_name = 'سفارشات'

    def ready(self):
        """رجیستر کردن سیگنال‌ها"""
        import apps.orders.signals  # noqa: F401
