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
# Create your models here.

# admin.site.register(MyUser)