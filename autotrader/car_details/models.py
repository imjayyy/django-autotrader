# Create your models here.
from django.db import models
from shipping.models import Country
from rest_framework import serializers
from djrichtextfield.models import RichTextField
import os

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
    color_hex = models.CharField(max_length=7,  null=True, blank=True)
    font_awesome_icon = models.TextField( null=True, blank=True)


    def __str__(self):
        return self.name_en

class Label(models.Model):
    name_az = models.TextField()
    name_en = models.TextField()
    color_hex = models.CharField(max_length=7, null=True, blank=True)
    font_awesome_icon = models.TextField( null=True, blank=True)
    
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
    feature_list =  models.ManyToManyField(Feature, related_name='vehicles')
    label_list = models.ManyToManyField(Label, related_name='vehicles')
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



def vehicle_image_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    # Use a temp name until we get the ID
    return f"vehicles/temp.{ext}"

class VehicleMedia(models.Model):
    vehicle_image_id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='vehicles/', null=True, blank=True) 
    api_id = models.IntegerField(null=True, blank=True)
    all_lots_id = models.BigIntegerField(null=True, blank=True)
    vin = models.TextField(null=True, blank=True)
    img_url_from_api = models.TextField(null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    image_path = models.CharField(null=True, blank=True, max_length=255)
    video_path = models.CharField(null=True, blank=True, max_length=255)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new and self.image:
            # Now rename the image to vehicle_image_id
            ext = os.path.splitext(self.image.name)[1]
            new_name = f"vehicles/{self.vehicle_image_id}{ext}"
            from django.core.files.storage import default_storage
            old_image = self.image
            new_image = default_storage.save(new_name, old_image)
            self.image.name = new_name
            super().save(update_fields=['image'])

    def __str__(self):
        return f"VehicleMedia {self.vehicle_image_id} - VIN: {self.vin}"


