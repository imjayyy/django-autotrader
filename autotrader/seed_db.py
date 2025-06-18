import os
import django
from datetime import date
from random import randint, choice
import random

# Set up Django environment
import sys
sys.path.append('/autotrader')  # Update with the actual path to your project
import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "autotrader.settings")  # Replace 'your_project' with your actual project name
import django
django.setup()

# Import your models
from car_details.models import Fuel, BodyStyle, Transmission, Status, Vehicle, Color, Country, Label, Make, Model, Drive, VehicleMedia



# Function to insert data
def insert_data(model, values):
    instances = []
    for value in values:
        obj, created = model.objects.get_or_create(name_az=value, defaults={'name_en': value})
        if created:
            instances.append(obj)
    return instances


def insert_models_make():
    CAR_MODELS = {
    "Mercedes": ["C-Class", "E-Class", "S-Class", "GLE", "G-Wagon"],
    "BMW": ["3 Series", "5 Series", "7 Series", "X5", "X7"],
    "Ford": ["Mustang", "F-150", "Explorer", "Escape", "Bronco"],
    "Toyota": ["Corolla", "Camry", "RAV4", "Highlander", "Tacoma"],
    "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Odyssey"]
    }

    for make_name, models in CAR_MODELS.items():
        make, _ = Make.objects.get_or_create(name=make_name)
        print(make)
        for model_name in models:
            Model.objects.get_or_create(name=model_name, make=make)       
    print("Data inserted successfully!")




def insert_sample_data():
    makes = ["Toyota", "Honda", "Ford", "BMW", "Mercedes"]
    body_styles = ["Sedan", "Hatchback", "SUV", "Truck"]
    transmissions = ["Automatic", "Manual"]
    fuels = ["Petrol", "Diesel", "Electric", "Hybrid"]
    statuses = ["New", "Used", "Certified"]
    countries = ["USA", "Canada", "Azerbaijan"]
    drive = ["Front Wheel Drive", "Rear Wheel Drive", "All Wheel Drive", "Four Wheel Drive"]
    colors = ["Red", "Blue", "Green", "Black", "White", "Silver", "Gray", "Yellow", "Orange", "Purple", "Brown", "Beige", "Gold", "Bronze", "Copper", "Pink", "Turquoise", "Lime", "Teal", "Magenta", "Violet", "Maroon", "Aquamarine", "Coral", "Salmon", "Khaki", "Indigo", "Azure", "Lavender", "Periwinkle", "Tan", "Thistle", "Plum", "Mauve", "Lilac", "Amber", "Ivory", "Crimson", "Fuchsia", "Wheat", "Lemon", "Peach", "Cream", "Lavender", "Cyan", "Mint", "Olive", "Apricot", "Navy", "Burgundy", "Emerald", "Sapphire", "Aqua", "Lemon", "Peach", "Lavender", "Cyan", "Mint", "Olive", "Apricot", "Navy", "Burgundy", "Emerald", "Sapphire", "Aqua"]
    
    for d in drive:
        Drive.objects.get_or_create(name_az=d, name_en=d)
    
    for color in colors:
        Color.objects.get_or_create(name_az=color, name_en=color)

    for make in makes:
        Make.objects.get_or_create(name=make)
    
    for bs in body_styles:
        BodyStyle.objects.get_or_create(name_az=bs, name_en=bs)
    
    for fuel in fuels:
        Fuel.objects.get_or_create(name_az=fuel, name_en=fuel)
    
    for country in countries:
        Country.objects.get_or_create(name=country)

    for transmission in transmissions:
        Transmission.objects.get_or_create(name_az=transmission, name_en=transmission)

    for status in statuses:
        Status.objects.get_or_create(name_az=status, name_en=status)

    for i in range(20):  # Insert 10 sample vehicles
        make = Make.objects.order_by('?').first()  # Select a random Make

        if make:  # Ensure Make exists
            model = Model.objects.filter(make_id=make).order_by('?').first()  # Get a valid Model for that Make
            
            if model:  # Ensure a model exists for the selected make
                fuel_ = Fuel.objects.order_by('?').first()

                if fuel_.id == 3:
                    Vehicle.objects.create(
                    make=make,
                    model=model,  # Select a Model that belongs to the Make
                    transmission=Transmission.objects.order_by('?').first(),
                    fuel=Fuel.objects.order_by('?').first(),
                    body_style=BodyStyle.objects.order_by('?').first(),
                    # country=Country.objects.order_by('?').first(),
                    VIN=f'VIN{randint(100000, 999999)}',
                    currency='USD',
                    # feature_list="GPS, Sunroof, Leather Seats",
                    number_of_seats=choice([2, 4, 5, 7]),
                    price=randint(5000, 50000),
                    # price_currency='USD',
                    is_popular=choice([True, False]),
                    supplier_id=1,
                    year=randint(2000, 2022),
                    odometer=randint(0, 200000),
                    zero_to_hundred = round(random.uniform(0.0, 10.0), 1),
                    motor_power = randint(0, 300),
                    motor_power_unit = "Kw/h",
                    battery_range = randint(0, 400),

                    is_published=True,
                    status=Status.objects.order_by('?').first(),
                    color_id=Color.objects.order_by('?').first().id,
                    country=Country.objects.order_by('?').first(),
                    drive_id=Drive.objects.order_by('?').first().id,
                )


                else:
                    Vehicle.objects.create(
                    make=make,
                    model=model,  # Select a Model that belongs to the Make
                    transmission=Transmission.objects.order_by('?').first(),
                    fuel=Fuel.objects.order_by('?').first(),
                    body_style=BodyStyle.objects.order_by('?').first(),
                    # country=Country.objects.order_by('?').first(),
                    VIN=f'VIN{randint(100000, 999999)}',
                    currency='USD',
                    # feature_list="GPS, Sunroof, Leather Seats",
                    number_of_seats=choice([2, 4, 5, 7]),
                    price=randint(5000, 50000),
                    # price_currency='USD',
                    is_popular=choice([True, False]),
                    supplier_id=1,
                    year=randint(2000, 2022),
                    odometer=randint(0, 200000),
                    engine_power=randint(1000, 3000),   
                    is_published=True,
                    status=Status.objects.order_by('?').first(),
                    color_id=Color.objects.order_by('?').first().id,
                    country=Country.objects.order_by('?').first(),
                    drive_id=Drive.objects.order_by('?').first().id,
                )

    print("Data inserted successfully!")

def insert_sample_vehicle_images():
    sample_image_urls = [
            "https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Y2FyfGVufDB8fDB8fHwy",
            "https://images.unsplash.com/photo-1503376780353-7e6692767b70?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8Y2FyfGVufDB8fDB8fHwy",
            "https://images.unsplash.com/photo-1511919884226-fd3cad34687c?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OXx8Y2FyfGVufDB8fDB8fHwy",
            "https://images.unsplash.com/photo-1567808291548-fc3ee04dbcf0?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTF8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1493238792000-8113da705763?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTR8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1485291571150-772bcfc10da5?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTd8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTl8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1507136566006-cfc505b114fc?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MjF8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1541443131876-44b03de101c5?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MjV8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mjh8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1502489597346-dad15683d4c2?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MzF8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1549927681-0b673b8243ab?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MzN8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1542362567-b07e54358753?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MzZ8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1555626906-fcf10d6851b4?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mzh8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1490641815614-b45106d6dd04?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NDB8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1502219422320-9ca47798b75b?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NDN8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NDd8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1517026575980-3e1e2dedeab4?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NTB8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1598586958772-8bf368215c2a?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NTN8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1618353482480-61ca5a9a7879?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NTh8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NjJ8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1489686995744-f47e995ffe61?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NjN8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1554294314-80a5fb7e6bd5?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NjZ8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1519752441410-d3ca70ecb937?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Njl8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1582639510494-c80b5de9f148?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NzR8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1591105327764-4c4b76f9e6a0?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nzd8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1609520505218-7421df70121d?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nzh8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1533106418989-88406c7cc8ca?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8ODF8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1608823240964-d7f1d8e2ac85?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8ODR8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1580274437636-1c384e59e9b5?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8ODZ8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1532268116505-8c59cc37d2e6?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8ODl8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1617624085810-3df2165bd11b?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OTF8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1464851707681-f9d5fdaccea8?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OTR8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1549207107-2704df6b92ab?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OTV8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1620157206955-5d8ebca0df95?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OTd8fGNhcnxlbnwwfHwwfHx8Mg%3D%3D",
            "https://images.unsplash.com/photo-1528659997310-540c4945fa73?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTAxfHxjYXJ8ZW58MHx8MHx8fDI%3D",
            "https://images.unsplash.com/photo-1567784430956-b42137db2920?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTA0fHxjYXJ8ZW58MHx8MHx8fDI%3D",
            "https://images.unsplash.com/photo-1593142871910-2a967580ecdc?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTA4fHxjYXJ8ZW58MHx8MHx8fDI%3D",
            "https://images.unsplash.com/photo-1613246922662-c0b007a418d5?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTEwfHxjYXJ8ZW58MHx8MHx8fDI%3D",
            "https://images.unsplash.com/photo-1594611342073-4bb7683c27ad?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTE0fHxjYXJ8ZW58MHx8MHx8fDI%3D",
            "https://images.unsplash.com/photo-1601827280216-d850636510e0?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTE3fHxjYXJ8ZW58MHx8MHx8fDI%3D",
            "https://images.unsplash.com/photo-1523676060187-f55189a71f5e?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTIwfHxjYXJ8ZW58MHx8MHx8fDI%3D",
            "https://images.unsplash.com/photo-1598248770508-3f58e0ff8ff3?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTIyfHxjYXJ8ZW58MHx8MHx8fDI%3D",
            "https://images.unsplash.com/photo-1588623259724-71e3e35834c9?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTI0fHxjYXJ8ZW58MHx8MHx8fDI%3D",
            "https://images.unsplash.com/photo-1588086272079-8b1556abdb53?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTI3fHxjYXJ8ZW58MHx8MHx8fDI%3D",
            "https://images.unsplash.com/photo-1508974239320-0a029497e820?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTI4fHxjYXJ8ZW58MHx8MHx8fDI%3D",
            "https://images.unsplash.com/photo-1606577924006-27d39b132ae2?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTMxfHxjYXJ8ZW58MHx8MHx8fDI%3D",
            "https://images.unsplash.com/photo-1523983519351-ab98a0abe560?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTM0fHxjYXJ8ZW58MHx8MHx8fDI%3D",
            "https://images.unsplash.com/photo-1612593968469-d44a2e6ab5d2?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTM2fHxjYXJ8ZW58MHx8MHx8fDI%3D",
            "https://images.unsplash.com/photo-1567863786964-9d65fa4469ed?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTQwfHxjYXJ8ZW58MHx8MHx8fDI%3D",
        
 ]

    vehicles = Vehicle.objects.all()
    for j in range(5):
        for i, vehicle in enumerate(vehicles):
            VehicleMedia.objects.create(
                vin=vehicle.VIN,
                img_url_from_api=choice(sample_image_urls),
                vehicle=vehicle,
                image_path="sample_images/car_image.jpg",
                video_path="sample_videos/car_video.mp4",
            )

    print("Sample vehicle images inserted successfully!")

def add_engine_type():
    vehicles = Vehicle.objects.all()
    for vehicle in vehicles:
        if vehicle.fuel.id == 3:
            types_ = ["BLDC", "AC Induction", "Switched Reluctance", "Permanent Magnet"]
            vehicle.engine_type = random.choice(types_)
        else:
            types_ = ["Inline", "V", "Flat", "W", "Rotary"]
            vehicle.engine_type = random.choice(types_)
        vehicle.save()
    print("Engine type added successfully!")


def add_discount():
    vehicles = Vehicle.objects.all()
    for vehicle in vehicles:
        array = [1000, 2000, 2500, 1500]
        vehicle.price_discount = random.choice(array)
        vehicle.save()
    print("Discount added successfully!")



# insert_models_make()
insert_sample_data()
insert_sample_vehicle_images()
add_discount()
add_engine_type()