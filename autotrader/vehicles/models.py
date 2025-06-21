from django.db import models
from django.db.models import JSONField
# from django.contrib.postgres.fields import models.TextField
from django.utils import timezone
import json

class CarInfo(models.Model):
    all_lots_id = models.BigIntegerField(unique=True)
    make = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    
    series = models.CharField(max_length=255, null=True, blank=True)
    vehicle_type = models.CharField(max_length=255, null=True, blank=True)
    body_class = models.CharField(max_length=255, null=True, blank=True)
    make_id = models.IntegerField(null=True, blank=True)
    model_id = models.IntegerField(null=True, blank=True)
    series_id = models.IntegerField(null=True, blank=True)
    vehicle_type_id = models.IntegerField(null=True, blank=True)
    body_class_id = models.IntegerField(null=True, blank=True)

class Vehicle(models.Model):
    lot_id = models.BigIntegerField(null=True, blank=True)
    vin = models.CharField(unique=True,max_length=255, null=True, blank=True, db_index=True)
    auction_name = models.CharField(max_length=255, null=True, blank=True)
    make = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    body_style = models.CharField(max_length=255, null=True, blank=True)
    car_keys = models.CharField(max_length=20, null=True, blank=True)
    color = models.CharField(max_length=255, null=True, blank=True)
    cylinders = models.CharField(max_length=20, null=True, blank=True)
    doc_type = models.CharField(max_length=255, null=True, blank=True)
    drive = models.CharField(max_length=255, null=True, blank=True)
    engine_type = models.CharField(max_length=255, null=True, blank=True)
    est_retail_value = models.FloatField(null=True, blank=True)
    fuel = models.CharField(max_length=255, null=True, blank=True)
    highlights = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255,blank=True, null=True) 
    lot_number = models.BigIntegerField(null=True, blank=True)
    odometer = models.FloatField(null=True, blank=True)
    primary_damage = models.CharField(max_length=255, null=True, blank=True)
    secondary_damage = models.CharField(max_length=255, null=True, blank=True)
    seller = models.CharField(max_length=255, null=True, blank=True)
    series = models.CharField(max_length=255, null=True, blank=True)
    transmission = models.CharField(max_length=255, null=True, blank=True)
    vehicle_type = models.CharField(max_length=255, null=True, blank=True)
    is_insurance = models.BooleanField(null=True, blank=True)
    currency_name = models.CharField(max_length=50, null=True, blank=True)
    currency_code = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True, default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True, default=timezone.now)

    # JSON / Flexible Data Fields
    car_photo_urls = models.TextField(models.URLField(), default=list, blank=True, null=True)
    damage_photos = models.TextField(models.URLField(), default=list, blank=True, null=True)
    buy_now_price_histories = models.JSONField(default=dict, blank=True, null=True)
    sales_history = models.JSONField(default=dict, blank=True, null=True)
    active_bidding = models.JSONField(default=dict, blank=True, null=True)
    buy_now_car = models.JSONField(default=dict, blank=True, null=True)

    car_info = models.ForeignKey('CarInfo', on_delete=models.SET_NULL, null=True, blank=True)

    to_be_updated = models.BooleanField(default=True)
    to_be_published = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            original = Vehicle.objects.get(pk=self.pk)
            if original.to_be_published is False and self.to_be_published != original.to_be_published:
                self.to_be_published = original.to_be_published
        super().save(*args, **kwargs)

    def set_car_photo_urls(self, value):
        self.car_photo_urls = json.dumps(value)

    def get_car_photo_urls(self):
        return json.loads(self.car_photo_urls)

    def set_damage_photos(self, value):
        self.damage_photos = json.dumps(value)

    def get_damage_photos(self):
        return json.loads(self.damage_photos)

class SuperuserLastSearch(models.Model):
    filters = models.JSONField(default=dict)
    job_cancelled = models.BooleanField(default=False)


    def __str__(self):
        return "Superuser Last Search Filters"