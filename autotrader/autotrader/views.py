from django.shortcuts import render
from car_details.serializers import VehicleSerializer
from car_details.models import Vehicle
from datetime import datetime
from car_details.models import Make, Model, Transmission, Drive, Fuel, BodyStyle, Color
from car_details.models import Country
from car_details.serializers import VehicleSerializer, MakeSerializer,VehicleDetailsSerializer, VehicleListSerializer
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from urllib.parse import urlencode
import re

def home(request):
    vehicles_in_az = Vehicle.objects.order_by("?")[:3]  # Fetch 3 random vehicles
    vehicles_in_az_serializer = VehicleListSerializer(vehicles_in_az, many=True)

    electric_vehicles = Vehicle.objects.filter(fuel = 3 ).order_by("?")[:3]  # Fetch 3 random vehicles
    electric_vehicles_serializer = VehicleListSerializer(electric_vehicles, many=True)

    # cars_on_auction = Vehicle.objects.order_by("?")[:3]  # Fetch 3 random vehicles
    # cars_on_auction_serializer = VehicleListSerializer(cars_on_auction, many=True)
    country = Country.objects.all()

    current_year = datetime.now().year 

    form_fields = {
    'year_range':  [current_year - i for i in range(30)],
    'makes'  : Make.objects.all(), 
    'country' : country,
    }






    return render(request, 'home.html', {"vehicles_in_az": vehicles_in_az_serializer.data, 
                                        "electric_vehicles": electric_vehicles_serializer.data,  
                                        # "cars_on_auction": cars_on_auction_serializer.data,
                                         "form_fields": form_fields})


def search_results(request):

    form_fields = {
        'make': list(Make.objects.values("id", "name")), 
        'Transmission': list(Transmission.objects.values("id", "name_en", "name_az")),
        'Drive': list(Drive.objects.values("id", "name_en", "name_az")),
        'Fuel': list(Fuel.objects.values("id", "name_en", "name_az")),
        'BodyStyle': list(BodyStyle.objects.values("id", "name_en", "name_az")),
        'Color': list(Color.objects.values("id", "name_en", "name_az")),        
        'country': list(Country.objects.values("id", "name")),        
    }
    query_params = request.GET.dict()
    # query_params= {key: value for key, value in query_params.items() if value}
    return render(request, 'search-results.html', {"form_fields": form_fields, 'query_params': query_params})


def search_filter(request):
    return render(request, 'search-filter.html')


def car_details(request):
    return render(request, 'car-details.html')


def customs_calculator(request):
    return render(request, 'customs-calculator.html')

def about_us(request):
    return render(request, 'about-us.html')


def order_shipping(request):
    return render(request, 'order-shipping.html')

def contact(request):
    return render(request, 'contact.html')


def normal_car_details(request, id):
    car = get_object_or_404(Vehicle, id=id)  # Fetch car details or return 404
    car_serializer = VehicleDetailsSerializer(car)
    vehicles_in_az = Vehicle.objects.order_by("?")[:3]  # Fetch 3 random vehicles
    vehicles_in_az_serializer = VehicleListSerializer(vehicles_in_az, many=True)
    return render(request, 'normal-car-details.html', {"car": car_serializer.data,
                                                       "vehicles_in_az": vehicles_in_az_serializer.data, 
                                                       })


def text_search(request):
    search_query_string = request.GET.get('searchByText', '').strip()
    params = ''
    if not search_query_string:
        return redirect('search-results')

    search_query = search_query_string.split(" ")

    for q in search_query:
        make_id = Make.objects.filter(name__icontains=q).values('id').first()
        if make_id:
            break
    for q in search_query:
        model_id = Model.objects.filter(name__icontains=q).values('id').first()
        if model_id:
            break

    # Split into words, e.g., "honda city 2024" -> ['honda', 'city', '2024']
    keywords = re.split(r'\s+', search_query_string.lower())

    # Identify year from keywords
    year_pattern = re.compile(r'^(19|20)\d{2}$')
    year = next((word for word in keywords if year_pattern.match(word)), None)

    data = {
        
    }
    if make_id:
        data["make"] = make_id['id']
    if model_id:    
        data["model"] = model_id['id']
    if year:
        data["year_min"] = year

    params = '?' + '&'.join([f"{key}={value}" for key, value in data.items()])
    url = reverse('search-results') + params

    if data == {}:
        # If no make, model, or year found, redirect to search-results empty page.
        return render(request, 'search-results-empty.html')
    return HttpResponseRedirect(url)

    return redirect('no-results')  # Fallback if nothing matched