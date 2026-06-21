from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_sitesettings_map_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='about_content',
            field=models.TextField(blank=True, verbose_name='متن کامل درباره ما'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='about_short',
            field=models.TextField(blank=True, verbose_name='متن کوتاه درباره ما'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='map_latitude',
            field=models.FloatField(default=32.660282, verbose_name='عرض جغرافیایی نقشه'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='map_longitude',
            field=models.FloatField(default=51.666233, verbose_name='طول جغرافیایی نقشه'),
        ),
    ]
