# Generated by Django 4.2.16 on 2025-04-21 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('car_details', '0012_rename_country_id_vehicle_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='date_updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
