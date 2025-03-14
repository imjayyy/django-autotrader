import os
import django
from datetime import date
from random import randint, choice

# Set up Django environment
import sys
sys.path.append('/autotrader')  # Update with the actual path to your project
import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "autotrader.settings")  # Replace 'your_project' with your actual project name
import django
django.setup()

# Import your models
from car_details.models import Fuel, BodyStyle, Transmission, Status, Vehicle, Color, Country, Label, Make, Model



# Function to insert data
def insert_data(model, values):
    instances = []
    for value in values:
        obj, created = model.objects.get_or_create(name_az=value, defaults={'name_en': value})
        if created:
            instances.append(obj)
    return instances

def insert_sample_data():
    makes = ["Toyota", "Honda", "Ford", "BMW", "Mercedes"]
    body_styles = ["Sedan", "Hatchback", "SUV", "Truck"]
    transmissions = ["Automatic", "Manual"]
    fuels = ["Petrol", "Diesel", "Electric", "Hybrid"]
    statuses = ["New", "Used", "Certified"]
    countries = ["USA", "Canada", "Germany"]

    # for make in makes:
    #     Make.objects.get_or_create(name_az=make, name_en=make)
    
    # for bs in body_styles:
    #     BodyStyle.objects.get_or_create(name_az=make, name_en=make)
    
    # for fuel in fuels:
    #     Fuel.objects.get_or_create(name_az=fuel, name_en=fuel)
    
    # for country in countries:
    #     Country.objects.get_or_create(name_az=country, name_en=country)

    for i in range(10):  # Insert 10 sample vehicles
        Vehicle.objects.create(
            make_id=Make.objects.order_by('?').first(),
            transmission=choice([1, 2]),
            fuel=Fuel.objects.order_by('?').first(),
            body_style=BodyStyle.objects.order_by('?').first(),
            country=Country.objects.order_by('?').first(),
            VIN=f'VIN{randint(100000, 999999)}',
            currency='USD',
            feature_list="GPS, Sunroof, Leather Seats",
            number_of_seats=choice([2, 4, 5, 7]),
            price=randint(5000, 50000),
            price_currency='USD',
            is_popular=choice([True, False]),
            supplier_id=1
        )

    print("Data inserted successfully!")


    # # Run the function
    # insert_data(Make, makes)
    # insert_data(BodyStyle, body_styles)
    # insert_data(Fuel, ["Petrol", "Diesel", "Electric", "Hybrid"])
    # insert_data(Transmission, ["Manual", "Automatic"])
    # insert_data(Country, ["USA", "Germany", "Japan"])
    # insert_data(Status, ["New", "Used", "Damaged"])
    # insert_data(Label, [{"name_az": "Luxury", "name_en": "Luxury", "label_color_hex": "#FFD700"}])

    # print("Data insertion completed successfully!")
    # print("Data inserted successfully!")  
