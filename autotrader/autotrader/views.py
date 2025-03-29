from django.shortcuts import render
from car_details.serializers import VehicleSerializer
from car_details.models import Vehicle
from datetime import datetime
from car_details.models import Make, Model, Transmission, Drive, Fuel, BodyStyle, Color
from car_details.models import Country
from car_details.serializers import VehicleSerializer, MakeSerializer,VehicleDetailsSerializer
from django.shortcuts import render, get_object_or_404


def home(request):
    random_vehicles_1 = Vehicle.objects.order_by("?")[:3]  # Fetch 3 random vehicles
    random_vehicles_1_serializer = VehicleSerializer(random_vehicles_1, many=True)
    country = Country.objects.all()

    current_year = datetime.now().year 

    form_fields = {
    'year_range':  [current_year - i for i in range(30)],
    'makes'  : Make.objects.all(), 
    'country' : country,
    }

    return render(request, 'home.html', {"car_data_1": random_vehicles_1_serializer.data, "form_fields": form_fields})


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
    print(query_params)
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


def normal_car_details(request, id):
    car = get_object_or_404(Vehicle, id=id)  # Fetch car details or return 404
    car_serializer = VehicleDetailsSerializer(car)
    return render(request, 'normal-car-details.html', {"car": car_serializer.data})