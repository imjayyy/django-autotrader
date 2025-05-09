from django.db import models
from accounts.models import MyUser
from rest_framework import serializers

# Create your models here.

class Order(models.Model):
    customer = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    vehicle = models.ForeignKey('car_details.Vehicle', on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(max_length=50, choices=[  ('Pending', 'Pending'), 
                                                        ('Processing', 'Processing'), 
                                                        ('Shipped', 'Shipped'), 
                                                        ('Delivered', 'Delivered'),
                                                        ('Cancelled', 'Cancelled'),
                                                        ('Nulled', 'Nulled')
                                                        ], default='Pending')                                                      
    def __str__(self):
        return f"Order {self.id} - {self.customer.first_name}"
    
class Callback(models.Model):
    name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Callback from {self.name} - {self.country_code}{self.phone} - "
    

class Information(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class InformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Information
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']