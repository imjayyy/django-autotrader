# Generated by Django 4.2.16 on 2025-05-20 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car_details', '0024_vehicle_cylinders'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='engine_power',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
