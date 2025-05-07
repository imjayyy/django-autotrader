# Create your models here.
from django.db import models
from shipping.models import Country
from rest_framework import serializers
from ckeditor.fields import RichTextField


class Fuel(models.Model):
    name_az = models.TextField()
    name_en = models.TextField()

    def __str__(self):
        return self.name_en

class BodyStyle(models.Model):
    name_az = models.TextField()
    name_en = models.TextField()

    def __str__(self):
        return self.name_en

class Transmission(models.Model):
    name_az = models.TextField()
    name_en = models.TextField()

    def __str__(self):
        return self.name_en

class Drive(models.Model):
    name_az = models.TextField()
    name_en = models.TextField()

    def __str__(self):
        return self.name_en

class Color(models.Model):
    name_az = models.TextField()
    name_en = models.TextField()

    def __str__(self):
        return self.name_en

class Status(models.Model):
    name_az = models.TextField()
    name_en = models.TextField()

    def __str__(self):
        return self.name_en

class Feature(models.Model):
    name_az = models.TextField()
    name_en = models.TextField()

    def __str__(self):
        return self.name_en

class Label(models.Model):
    name_az = models.TextField()
    name_en = models.TextField()
    label_color_hex = models.CharField(max_length=7)

    def __str__(self):
        return self.name_en

class Make(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name

class Model(models.Model):
    make = models.ForeignKey(Make, on_delete=models.CASCADE)    
    name = models.TextField()

    def __str__(self):
        return f"{self.make.name} {self.name}"



class Vehicle(models.Model):
    make = models.ForeignKey(Make, on_delete=models.CASCADE)
    model = models.ForeignKey(Model, on_delete=models.CASCADE)
    fuel = models.ForeignKey(Fuel, on_delete=models.CASCADE)
    body_style = models.ForeignKey(BodyStyle, on_delete=models.CASCADE)
    transmission = models.ForeignKey(Transmission, on_delete=models.CASCADE)
    drive = models.ForeignKey(Drive, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    feature_list = models.TextField(blank=True, null=True)
    label_list = models.TextField(blank=True, null=True)
    odometer = models.IntegerField()
    zero_to_hundred = models.IntegerField(blank=True, null=True)
    motor_power = models.IntegerField(blank=True, null=True)
    motor_power_unit = models.CharField(max_length=50, blank=True, null=True)
    battery_range = models.IntegerField(blank=True, null=True)
    year = models.IntegerField()
    engine_power_unit = models.CharField(max_length=50,blank=True, null=True)
    engine_power = models.IntegerField(blank=True, null=True)
    comment = RichTextField(blank=True, null=True)
    VIN = models.TextField()
    currency = models.TextField()
    price_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price = models.FloatField()
    number_of_seats = models.IntegerField()
    is_published = models.BooleanField()
    documents = models.TextField(blank=True, null=True)
    is_popular = models.BooleanField()
    supplier_id = models.BigIntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.model} ({self.year})"

class VehicleMedia(models.Model):
    vehicle_image_id = models.AutoField(primary_key=True)
    api_id = models.IntegerField(null=True)
    all_lots_id = models.BigIntegerField(null=True)
    vin = models.TextField(null=True)
    img_url_from_api = models.TextField(null=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    image_path = models.CharField(null=True, max_length=255)
    video_path = models.CharField(null=True, max_length=255)

    def __str__(self):
        return f"VehicleMedia {self.vehicle_image_id} - VIN: {self.vin}"


