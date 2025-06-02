from django.shortcuts import render
from car_details.serializers import VehicleSerializer
from car_details.models import Vehicle
from datetime import datetime
from car_details.models import Make, Model, Transmission, Drive, Fuel, BodyStyle, Color
from car_details.models import Country
from car_details.serializers import VehicleSerializer, MakeSerializer,VehicleDetailsSerializer, VehicleListSerializer
from general.models import Order, Callback, Information, InformationSerializer
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.shortcuts import redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from urllib.parse import urlencode
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt

import re


ADMIN_USER_EMAIL= settings.ADMIN_USER_EMAIL
EMAIL_HOST_USER = settings.EMAIL_HOST_USER


def is_valid_phone_number(phone_number):
    # pattern = r'^[\d\s\-/]+$'    
    # return bool(re.match(pattern, phone_number))
    return not re.search(r'[^\d\s\-/]', phone_number)


def home(request):
    if request.method == "POST" and "Callback" in request.POST:
        pass
    vehicles_in_az = Vehicle.objects.filter(country = 3, is_popular = True, is_published = True).order_by("?")[:3]  # Fetch 3 random vehicles
    vehicles_in_az_serializer = VehicleListSerializer(vehicles_in_az, many=True)

    electric_vehicles = Vehicle.objects.filter(fuel = 3, is_popular = True, is_published = True ).order_by("?")[:3]  # Fetch 3 random vehicles
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

@csrf_exempt
def form_submission(request):
    name = request.POST.get("name")
    country_code = request.POST.get("country_code")
    phone = request.POST.get("phone")


    # Optionally, add server-side validation
    if name and country_code and phone:
        # Here you can save it to DB, send an email, or trigger any logic

        print(f"Callback Request: {name}, {country_code} {phone}")


        send_mail(
            "Call back request from AutoTrader django website",
            f"Callback Request: {name}, {country_code} {phone}",
            EMAIL_HOST_USER,
            [ADMIN_USER_EMAIL],
            fail_silently=False,
        )
        Callback.objects.create(
            name=name,
            country_code=country_code,
            phone=phone
        )
        return JsonResponse({"status": "success", "message": "Your callback request has been submitted!"})    
    elif not is_valid_phone_number(phone):
        return JsonResponse({"status": "error", "message": "Invalid phone number format."})
    else:
        return JsonResponse({"status": "error", "message": "Please fill in all fields."})


def search_results(request):

    form_fields = {
        'make': list(Make.objects.values("id", "name")), 
        'Transmission': list(Transmission.objects.values("id", "name_en", "name_az")),
        'Drive': list(Drive.objects.values("id", "name_en", "name_az")),
        'Fuel': list(Fuel.objects.values("id", "name_en", "name_az")),
        'BodyStyle': list(BodyStyle.objects.values("id", "name_en", "name_az")),
        'Color': list(Color.objects.values("id", "name_en", "name_az")),        
        'country': list(Country.objects.values("id", "name")),
        'engine_type': list(Vehicle.objects.values_list("engine_type", flat=True).distinct()) ,       
    }
    query_params = request.GET.dict()
    if "make" in query_params:
        if query_params.get('make') != 'any' and  query_params.get('model') != 'any':
            try:
                make_id_list = query_params.get('make').split(",")
            except ValueError:
                make_id_list = []
            if 'model' in query_params:
                try:
                    model_id_list = query_params.get('model').split(",")
                except ValueError:
                    model_id_list = []
                vehicles = Vehicle.objects.filter(make__id__in=make_id_list, model__id__in=model_id_list, is_published=True)
                form_fields.update({
                    'Transmission': list(Transmission.objects.filter(id__in=vehicles.values_list('transmission_id', flat=True).distinct()).values("id", "name_en", "name_az")),
                    'Drive': list(Drive.objects.filter(id__in=vehicles.values_list('drive_id', flat=True).distinct()).values("id", "name_en", "name_az")),
                    'Fuel': list(Fuel.objects.filter(id__in=vehicles.values_list('fuel_id', flat=True).distinct()).values("id", "name_en", "name_az")),
                    'BodyStyle': list(BodyStyle.objects.filter(id__in=vehicles.values_list('body_style_id', flat=True).distinct()).values("id", "name_en", "name_az")),
                    'Color': list(Color.objects.filter(id__in=vehicles.values_list('color_id', flat=True).distinct()).values("id", "name_en", "name_az")),
                    'country': list(Country.objects.filter(id__in=vehicles.values_list('country_id', flat=True).distinct()).values("id", "name")),
                    'engine_type': list(vehicles.values_list("engine_type", flat=True).distinct())
                })
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
    if request.method == "POST" and "Callback" in request.POST:
        name = request.POST.get("name")
        country_code = request.POST.get("country_code")
        phone = request.POST.get("phone")

        # Optionally, add server-side validation
        if name and country_code and phone:
            # Here you can save it to DB, send an email, or trigger any logic
            # For now, we'll just print it (or you can save it)

            print(f"Callback Request: {name}, {country_code} {phone}")
            ADMIN_USER_EMAIL= settings.ADMIN_USER_EMAIL
            EMAIL_HOST_USER = settings.EMAIL_HOST_USER

            send_mail(
                "Call back request from AutoTrader django website",
                f"Callback Request: {name}, {country_code} {phone}",
                EMAIL_HOST_USER,
                [ADMIN_USER_EMAIL],
                fail_silently=False,
            )
            Callback.objects.create(
                name=name,
                country_code=country_code,
                phone=phone
            )
                        # Show a success message
            # messages.success(request, "Your callback request has been submitted!")
            return render(request, 'thank-you.html')  # Redirect to avoid form resubmission
        else:
            messages.error(request, "Please fill in all fields.")
    return render(request, 'contact.html')

def information(request):
    information = Information.objects.all().order_by("-created_at")
    information_serializer = InformationSerializer(information, many=True)
    return render(request, 'information.html', {"information_data": information_serializer.data})

def information_view(request, id):
    information = get_object_or_404(Information, id=id)  # Fetch car details or return 404    
    information_serializer = InformationSerializer(information)

    return render(request, 'information-view.html', {"information_data": information_serializer.data})

def normal_car_details(request, id):
    car = get_object_or_404(Vehicle, id=id, is_published=True)  # Fetch car details or return 404

    car_serializer = VehicleDetailsSerializer(car)
    vehicles_in_az = Vehicle.objects.filter(is_published = True, model__id = car.model.id ).order_by("?")[:3]  # Fetch 3 random vehicles
    vehicles_in_az_serializer = VehicleListSerializer(vehicles_in_az, many=True)

    car_serializer_data = car_serializer.data

    car_serializer_data['price_azn'] = (float(car.price) * 1.7) 
    if car.price_discount :
        car_serializer_data['price'] = float(car.price) - float(car.price_discount)
        car_serializer_data['before_discount_price'] = (float(car.price))
        car_serializer_data['price_azn'] = (float(car_serializer_data['price']) * 1.7) 

    print(car_serializer_data)

    return render(request, 'normal-car-details.html', {"car": car_serializer_data,
                                                       "vehicles_in_az": vehicles_in_az_serializer.data, 
                                                       })

@login_required
def create_order(request, id):
    car = get_object_or_404(Vehicle, id=id)
    order = Order.objects.create(
        customer=request.user,
        vehicle=car,
        status='Pending'
    )
    send_mail(
                "Order request from AutoTrader django website",
                f"Order Request: {order.customer.first_name} {order.customer.last_login}, for {order.customer.phone} {order.vehicle.make.name} {order.vehicle.model.name} {order.vehicle.year}", 
                EMAIL_HOST_USER,
                [ADMIN_USER_EMAIL],
                fail_silently=False,
            )
    # Redirect to a success page or render a template
    return render(request, 'thank-you.html')

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
            make_id = Model.objects.filter(name__icontains=q).values('make').first()
            make_id = Make.objects.filter(id=make_id['make']).values('id').first()
            break

    # Split into words, e.g., "honda city 2024" -> ['honda', 'city', '2024']
    keywords = re.split(r'\s+', search_query_string.lower())

    # Identify year from keywords
    year_pattern = re.compile(r'^(19|20)\d{2}$')
    year = next((word for word in keywords if year_pattern.match(word)), None)

    data = {}
    if make_id:
        data["make"] = make_id['id']
    if model_id:    
        data["model"] = model_id['id']
    if year:
        data["year_min"] = year

    params = '?' + '&'.join([f"{key}={value}" for key, value in data.items()])
    url = reverse('search-results') + params

    print("Data: " , data )

    if data == {}:
        # If no make, model, or year found, redirect to search-results empty page.
        return render(request, 'search-results-empty.html')
    return HttpResponseRedirect(url)