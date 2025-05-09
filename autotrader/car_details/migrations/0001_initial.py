# Generated by Django 4.2.16 on 2025-03-13 18:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BodyStyle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_az', models.TextField()),
                ('name_en', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_az', models.TextField()),
                ('name_en', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_id', models.IntegerField()),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Drive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_az', models.TextField()),
                ('name_en', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_az', models.TextField()),
                ('name_en', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Fuel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_az', models.TextField()),
                ('name_en', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_az', models.TextField()),
                ('name_en', models.TextField()),
                ('label_color_hex', models.CharField(max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='Make',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('make_id', models.IntegerField()),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_az', models.TextField()),
                ('name_en', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Transmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_az', models.TextField()),
                ('name_en', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature_list', models.TextField()),
                ('label_list', models.TextField()),
                ('odometer', models.IntegerField()),
                ('year', models.DateField()),
                ('engine_power_unit', models.CharField(max_length=50)),
                ('engine_power', models.IntegerField()),
                ('comment', models.TextField()),
                ('VIN', models.TextField()),
                ('currency', models.TextField()),
                ('price_discount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price', models.FloatField()),
                ('number_of_seats', models.IntegerField()),
                ('is_published', models.BooleanField()),
                ('documents', models.TextField()),
                ('is_popular', models.BooleanField()),
                ('supplier_id', models.BigIntegerField()),
                ('body_style', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='car_details.bodystyle')),
                ('color', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='car_details.color')),
                ('country_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='car_details.country')),
                ('drive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='car_details.drive')),
                ('fuel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='car_details.fuel')),
                ('make_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='car_details.make')),
                ('model_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='car_details.model')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='car_details.status')),
                ('transmission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='car_details.transmission')),
            ],
        ),
    ]
