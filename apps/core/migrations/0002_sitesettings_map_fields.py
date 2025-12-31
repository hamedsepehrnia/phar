from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='map_latitude',
            field=models.FloatField(default=32.661443, verbose_name='عرض جغرافیایی نقشه'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='map_longitude',
            field=models.FloatField(default=51.666552, verbose_name='طول جغرافیایی نقشه'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='map_zoom',
            field=models.PositiveSmallIntegerField(default=14, verbose_name='زوم نقشه'),
        ),
    ]
