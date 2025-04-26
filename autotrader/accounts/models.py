from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib import admin

class MyUser(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

      # Add extra fields if needed
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

class Favorite(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    vehicle = models.ForeignKey('car_details.Vehicle', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Favorite"
        verbose_name_plural = "Favorites"

    def __str__(self):
        return f"{self.user.email} - {self.vehicle.name}"  # Assuming Vehicle has a 'name' field
    
class Orders(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    vehicle = models.ForeignKey('car_details.Vehicle', on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('canceled', 'Canceled')], default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    # Add any other fields you need for the order]

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order {self.id} by {self.user.email}"  # Assuming Vehicle has a 'name' field
