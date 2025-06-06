# Generated by Django 4.2.16 on 2025-05-07 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car_details', '0013_vehicle_date_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='documents',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='feature_list',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='label_list',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='price_discount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='supplier_id',
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
