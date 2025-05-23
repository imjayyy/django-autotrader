# Generated by Django 4.2.16 on 2025-05-18 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car_details', '0022_status_color_hex_status_font_awesome_icon_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='engine_power',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='zero_to_hundred',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=5, null=True),
        ),
    ]
