from django.db import models
from django.contrib import admin
# Create your models here.
class Country(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name
    
admin.site.register(Country)