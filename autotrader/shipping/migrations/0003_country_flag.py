# Generated by Django 4.2.16 on 2025-05-14 02:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0002_remove_country_country_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='flag',
            field=models.ImageField(blank=True, null=True, upload_to='flags/'),
        ),
    ]
