from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage
from car_details.models import Make, Model
from django.http import JsonResponse
from car_details.models import Vehicle, Country, Make, Model, VehicleMedia, Fuel, BodyStyle, Transmission, Drive, Color, Status, Feature, Label
from car_details.serializers import VehicleSerializer, VehicleListSerializer
# Create your views here.



def get_car_models(request, make):
    try:
        car_make = Make.objects.get(id__iexact=make)  # Case-insensitive match
        models = Model.objects.filter(make=car_make).values('id'  , 'name')
        return JsonResponse(list(models), safe=False)
    except Make.DoesNotExist:
        return JsonResponse([], safe=False)
    
def get_car_models_from_id(request):
    try:
        makes = request.GET.getlist("makes[]")
        car_make = Make.objects.filter(id__in=makes)  # Case-insensitive match
        models = list(Model.objects.filter(make__in=car_make).values('id'  , 'name'))
        return JsonResponse(list(models), safe=False)
    except Make.DoesNotExist:
        return JsonResponse([], safe=False)
    

def search_api(request):
    filters = {}

    print(request.GET)
    # Get filter parameters from request
    page= request.GET.get("page")
    make = request.GET.getlist("make[]")
    model = request.GET.getlist("model[]")
    countrys = request.GET.getlist("country[]")
    year_from = request.GET.get("year_from")
    year_to = request.GET.get("year_to")
    fuel = request.GET.getlist("fuels[]")
    body_style = request.GET.getlist("body_style[]")
    transmission = request.GET.getlist("transmission[]")
    drive = request.GET.getlist("drives[]")
    color = request.GET.getlist("color[]")
    price_min = request.GET.get("priceMin")
    price_max = request.GET.get("priceMax")
    odometerMax = request.GET.get("odometerMax")
    odometerMin = request.GET.get("odometerMin")
    year_min = request.GET.get("year_min")
    year_max = request.GET.get("year_max")
    # is_published = request.GET.get("is_published")

    # Convert lists of IDs to integers
    make = [int(m) for m in make if m.isdigit()]
    model = [int(m) for m in model if m.isdigit()]
    fuel = [int(f) for f in fuel if f.isdigit()]
    transmission = [int(t) for t in transmission if t.isdigit()]
    drive = [int(d) for d in drive if d.isdigit()]
    color = [int(c) for c in color if c.isdigit()]
    body_style = [int(b) for b in body_style if b.isdigit()]
    country = [int(c) for c in countrys if c.isdigit()]


    # Apply filters
    # if make and make != "any": 
    #     filters["make"] = Make.objects.filter(id__in=make)
    # if model and model != "any":
    #     filters["model"] =  Model.objects.filter(id__in=model)
    # if country and country != "any":        
    #     filters["country"] = Country.objects.filter(id__in=country)
    # if year_from and year_from != "any":
    #     filters["year__gte"] = int(year_from)
    # if year_to and year_to != "any":
    #     filters["year__lte"] = int(year_to)
    # if fuel and fuel != "any":
    #     filters["fuel"] = Fuel.objects.filter(id__in=fuel)
    # if body_style and body_style != "any":
    #     filters["body_style"] = body_style
    # if transmission and transmission != "any":
    #     filters["transmission"] = Transmission.objects.filter(id__in=transmission)
    # if drive and drive != "any":
    #     filters["drive"] = Drive.objects.filter(id__in=drive)
    # if color and color != "any":
    #     filters["color"] = Color.objects.filter(id__in=color)
    # if odometerMax and odometerMax != "any":
    #     filters["odometer__lte"] = int(odometerMax)
    # if odometerMin and odometerMin != "any":    
    #     filters["odometer__gte"] = int(odometerMin)
    # if price_min and price_min != "any":
    #     filters["price__gte"] = float(price_min)
    # if price_max and price_max != "any":
    #     filters["price__lte"] = float(price_max)

    if make:
        filters["make__id__in"] = make
    if model:
        filters["model__id__in"] = model
    if country:
        filters["country__id__in"] = country
    if year_from:
        filters["year__gte"] = int(year_from)
    if year_to:
        filters["year__lte"] = int(year_to)
    if fuel:
        filters["fuel__id__in"] = fuel
    if body_style:
        filters["body_style__id__in"] = body_style
    if transmission:
        filters["transmission__id__in"] = transmission
    if drive:
        filters["drive__id__in"] = drive
    if color:
        filters["color__id__in"] = color
    if odometerMax:
        filters["odometer__lte"] = int(odometerMax)
    if odometerMin:
        filters["odometer__gte"] = int(odometerMin)
    if price_min:
        filters["price__gte"] = float(price_min)
    if price_max:
        filters["price__lte"] = float(price_max)
    if country:
        filters["country__id__in"] = country
    if year_min and year_min != "any":
        filters["year__gte"] = int(year_min)
    if year_max and year_max != "any":
        filters["year__lte"] = int(year_max)
    
    filters["is_published"] = True
    # Query database with optimized field selection
    # vehicles = Vehicle.objects.filter(**filters)
    # vehicles_serializer = VehicleListSerializer(vehicles, many=True)


    vehicles_qs = Vehicle.objects.filter(**filters)
    sorting_order = request.GET.get("sorting_order")
    sorting_by = request.GET.get("sorting_by")
    if sorting_by != "None" and sorting_by != None:       
       if sorting_order == "asc":
            vehicles_qs = vehicles_qs.order_by(sorting_by)
       else:
            vehicles_qs = vehicles_qs.order_by("-" + sorting_by)
            

    page = int(request.GET.get('page', 1))
    paginator = Paginator(vehicles_qs, 10)  # 10 per page



    try:
        page_obj = paginator.page(page)
    except EmptyPage:
        return JsonResponse({'detail': 'Page not found'}, status=404)

    serializer = VehicleListSerializer(page_obj.object_list, many=True)

    return JsonResponse({
        'count': paginator.count,
        'num_pages': paginator.num_pages,
        'current_page': page,
        'results': serializer.data,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
    }, safe=False)
    # return JsonResponse(list(vehicles_serializer.data), safe=False)

