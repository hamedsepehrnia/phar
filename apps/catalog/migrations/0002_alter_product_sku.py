from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='sku',
            field=models.CharField(
                blank=True,
                max_length=50,
                null=True,
                unique=True,
                verbose_name='کد کالا (SKU)',
            ),
        ),
    ]
