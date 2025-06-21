# views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .scheduler import is_scheduler_enabled,set_scheduler_state
from .utils import  get_field_counts, get_buy_now_options 
from django.http import Http404
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.utils import timezone
from collections import defaultdict
import json,requests,time,random
from .models import Vehicle, SuperuserLastSearch,CarInfo
import csv,io,re
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .services import update_or_create_car_info, save_vehicle_data,fetch_car_vin_data,fetch_data_with_retry_manuall
from datetime import datetime, timedelta
from django.db.models.functions import Lower, Trim
from vehicles.scheduler import start_scheduler,get_last_job_filters,get_job_timestamps
from vehicles.utils import get_all_to_be_updated
from django.core.cache import cache

default_token = '6394dc91ece3542af402645dc9f2aa1b2c2dec923b24cf3d249373228a019684'

HEADERS = {
    "Authorization": f"Bearer {default_token}",  # Assuming it's a Bearer token for authorization
    "Content-Type": "application/json",  # Set the correct content type if needed
}

def admin_required(user):
    return user.is_superuser

@login_required
@user_passes_test(admin_required)
def get_vehicle_view_form(request):
    api_token = default_token
    filters = get_last_job_filters()
    yesterday = (datetime.now() - timedelta(days=1)).date()

    # Grab latest values from last job or use default

    per_page = filters.get('per_page', 50)
    page = filters.get('page', 1)
    timestamps = get_job_timestamps()
    auction_date_from = timestamps.get("start") or yesterday
    auction_date_to = timestamps.get("end") or yesterday

    # Load the saved filters if available
    try:
        saved_filters = SuperuserLastSearch.objects.first().filters
    except AttributeError:
        saved_filters = {}

    return render(request, 'get-vehicle-form.html', {
        'api_token': api_token,
        'scheduler_enabled': is_scheduler_enabled(),
        'summary': None,
        'page': page,
        'auction_date_from': auction_date_from,
        'auction_date_to': auction_date_to,
        'saved_filters': saved_filters,
        'per_page': per_page,
    })


@login_required
@user_passes_test(admin_required)
def toggle_scheduler(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "enable":
            set_scheduler_state(True)
            messages.success(request, "Scheduler has been enabled.")
            start_scheduler()  # Make sure scheduler starts if not already running
        elif action == "disable":
            set_scheduler_state(False)
            messages.warning(request, "Scheduler has been disabled.")
        else:
            messages.error(request, "Invalid scheduler action.")
    return redirect('get_vehicle') 

# import threading

# @login_required
# @user_passes_test(admin_required)
# def toggle_scheduler(request):
#     if request.method == "POST":
#         action = request.POST.get("action")
#         if action == "enable":
#             set_scheduler_state(True)
#             messages.success(request, "Scheduler has been enabled.")
#             start_scheduler()  # Make sure scheduler thread is running
#             # 🚀 Immediately trigger the job in a thread (so it doesn't block request)
#             threading.Thread(target=run_daily_fetch, daemon=True).start()
#         elif action == "disable":
#             set_scheduler_state(False)
#             messages.warning(request, "Scheduler has been disabled.")
#         else:
#             messages.error(request, "Invalid scheduler action.")
#     return redirect('get_vehicle')


# ###################### FRONTEND   ###########################

def parse_date_safe(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return None

def index(request):
    current_time = now()
    vehicles_qs = Vehicle.objects.all()

    # Get and normalize filters
    def norm(val):
        return val.strip().lower() if val else None

    selected_make = norm(request.GET.get('make'))
    selected_model = norm(request.GET.get('model'))
    selected_auction = norm(request.GET.get('auction'))
    selected_primary_damage = norm(request.GET.get('primary_damage'))
    sale_date_from = parse_date_safe(request.GET.get('sale_date_from'))
    sale_date_to = parse_date_safe(request.GET.get('sale_date_to'))

    # Annotate cleaned fields for filtering
    vehicles_qs = vehicles_qs.annotate(
        make_clean=Trim(Lower('make')),
        model_clean=Trim(Lower('model')),
        auction_clean=Trim(Lower('auction_name')),
        damage_clean=Trim(Lower('primary_damage')),
    )

    if selected_make and selected_make != "all makes":
        vehicles_qs = vehicles_qs.filter(make_clean=selected_make)
    if selected_model and selected_model != "all models":
        vehicles_qs = vehicles_qs.filter(model_clean=selected_model)
    if selected_auction and selected_auction != "all auctions":
        vehicles_qs = vehicles_qs.filter(auction_clean=selected_auction)
    if selected_primary_damage and selected_primary_damage != "damage type":
        vehicles_qs = vehicles_qs.filter(damage_clean=selected_primary_damage)
    if sale_date_from and sale_date_from <= current_time.date():
        vehicles_qs = vehicles_qs.filter(created_at__date__gte=sale_date_from)
    if sale_date_to and sale_date_to >= (sale_date_from or sale_date_to):
        vehicles_qs = vehicles_qs.filter(created_at__date__lte=sale_date_to)

    # Only load required fields
    vehicles_qs = vehicles_qs.only('id', 'make', 'model', 'year', 'location', 'primary_damage', 'car_photo_urls', 'created_at', 'est_retail_value')

    # Pagination (only 15 per page)
    paginator = Paginator(vehicles_qs, 15)
    page_number = request.GET.get('page')
    vehicles_page = paginator.get_page(page_number)

    # Enrich paginated vehicles with photos
    for vehicle in vehicles_page:
        raw_photos = getattr(vehicle, 'car_photo_urls', None)
        if isinstance(raw_photos, str):
            car_photos = [url.strip().strip('"') for url in raw_photos.strip('{}').split(',') if url.strip()]
        elif isinstance(raw_photos, list):
            car_photos = raw_photos
        else:
            car_photos = []
        vehicle.car_photos = car_photos
        vehicle.primary_photo = car_photos[0] if car_photos else None

    # Top Picks from "NORMAL WEAR"
    normal_wear_qs = vehicles_qs.filter(damage_clean='normal wear')[:100]
    normal_wear = list(normal_wear_qs)
    top_picks = random.sample(normal_wear, k=20) if len(normal_wear) >= 20 else normal_wear

    if len(top_picks) < 20:
        excluded_ids = [v.id for v in top_picks]
        remaining_qs = vehicles_qs.exclude(id__in=excluded_ids)[:100]
        remaining = list(remaining_qs)
        top_picks.extend(random.sample(remaining, k=min(20 - len(top_picks), len(remaining))))

    # Enrich top_picks with photo URLs
    for vehicle in top_picks:
        raw_photos = getattr(vehicle, 'car_photo_urls', None)
        if isinstance(raw_photos, str):
            car_photos = [url.strip().strip('"') for url in raw_photos.strip('{}').split(',') if url.strip()]
        elif isinstance(raw_photos, list):
            car_photos = raw_photos
        else:
            car_photos = []
        vehicle.car_photos = car_photos
        vehicle.primary_photo = car_photos[0] if car_photos else None

    # Caching make/model/auction/damage counts for reuse
    make_counts = cache.get('make_counts')
    if not make_counts:
        make_counts = Vehicle.objects.values('make').annotate(count=Count('make')).order_by('make')
        cache.set('make_counts', make_counts, 60 * 10)

    model_counts = cache.get('model_counts')
    if not model_counts:
        model_counts = Vehicle.objects.values('model').annotate(count=Count('model')).order_by('model')
        cache.set('model_counts', model_counts, 60 * 10)

    auction_counts = cache.get('auction_counts')
    if not auction_counts:
        auction_counts = Vehicle.objects.values('auction_name').annotate(count=Count('auction_name')).order_by('auction_name')
        cache.set('auction_counts', auction_counts, 60 * 10)

    damage_counts = cache.get('damage_counts')
    if not damage_counts:
        damage_counts = Vehicle.objects.values('primary_damage').annotate(count=Count('primary_damage')).order_by('primary_damage')
        cache.set('damage_counts', damage_counts, 60 * 10)

    makes = sorted({item['make'].title() for item in make_counts if item['make']})
    models = sorted({item['model'].title() for item in model_counts if item['model']})
    auctions = sorted({item['auction_name'].title() for item in auction_counts if item['auction_name']})
    damages = sorted({item['primary_damage'].title() for item in damage_counts if item['primary_damage']})

    # Year dropdown options
    years = cache.get('years_list')
    if not years:
        years = list(Vehicle.objects.filter(to_be_published=True).exclude(year__isnull=True).values_list('year', flat=True).distinct())
        cache.set('years_list', years, 60 * 30)

    context = {
        'vehicles': vehicles_page,
        'top_picks': top_picks,
        'makes': makes,
        'models': models,
        'auctions': auctions,
        'damages': damages,
        'make_counts': [{'make': m['make'].title(), 'count': m['count']} for m in make_counts],
        'model_counts': [{'model': m['model'].title(), 'count': m['count']} for m in model_counts if m['model']],

        'auction_counts': [{'make': m['auction_name'].title(), 'count': m['count']} for m in auction_counts],
        'damage_counts': [{'make': m['primary_damage'].title(), 'count': m['count']} for m in damage_counts],
        'selected_make': selected_make,
        'selected_model': selected_model,
        'selected_auction': selected_auction,
        'selected_primary_damage': selected_primary_damage,
        'sale_date_from': sale_date_from,
        'sale_date_to': sale_date_to,
        'now': current_time,
        'years_asc': sorted(years),
        'years_desc': sorted(years, reverse=True),
        'total_vehicle_count': Vehicle.objects.count()
    }

    return render(request, 'index.html', context)


def get_filtered_options(request):
    make = request.GET.get('make')
    model = request.GET.get('model')

    filters = {'to_be_published': True}
    if make:
        filters['make__iexact'] = make
    if model:
        filters['model__iexact'] = model

    vehicles = Vehicle.objects.filter(**filters)

    # Get distinct values for each field based on filtered vehicles
    auctions = list(vehicles.values_list('auction_name', flat=True).distinct())
    years = sorted(set(vehicles.values_list('year', flat=True)))
    damages = list(vehicles.values_list('primary_damage', flat=True).distinct())

    return JsonResponse({
        'auctions': auctions,
        'years': years,
        'damages': damages,
    })


def vehicle_list(request):
    now = datetime.now()
    sort_field = request.GET.get('sort')
    sort_order = request.GET.get('order', 'asc')
    vehicles_qs = Vehicle.objects.filter(to_be_published=True)

    if not sort_field:
        vehicles_qs = vehicles_qs.order_by('-created_at')

    def get_list(param):
        return [v.strip() for v in request.GET.getlist(param) if v]

    # Filters
    damage = request.GET.get('damage')
    selected_primary_damage = request.GET.get('primary_damage')

    damage = damage.strip().lower() if damage else None
    selected_primary_damage = selected_primary_damage.strip().lower() if selected_primary_damage else None

    if damage and damage != "damage type":
        vehicles_qs = vehicles_qs.annotate(damage_clean=Trim(Lower('primary_damage'))).filter(damage_clean=damage)
    if selected_primary_damage and selected_primary_damage != "damage type":
        vehicles_qs = vehicles_qs.annotate(damage_clean=Trim(Lower('primary_damage'))).filter(damage_clean=selected_primary_damage)

    newly_added = get_list('newly_added')
    sale_status_filter = get_list('sale_status')
    engine_type = [v.lower() for v in get_list('engine_type')]
    fuel_type = [v.lower() for v in get_list('fuel_type')]
    color = [v.lower() for v in get_list('color')]
    primary_damage = [v.lower() for v in get_list('primary_damage')]
    secondary_damage = [v.lower() for v in get_list('secondary_damage')]
    transmission = [v.lower() for v in get_list('transmission')]
    cylinders = [v.lower() for v in get_list('cylinders')]
    body_style = [v.lower() for v in get_list('body_style')]
    selected_vehicle_types = [v.lower() for v in get_list('vehicle_type')]
    seller = [v.lower() for v in get_list('seller')]
    buy_now = [v.lower() for v in get_list('buy_now')]
    driveline = [v.lower() for v in get_list('driveline')]
    location = [v.lower() for v in get_list('location')]
    buyer_country = [v.lower() for v in get_list('buyer_country')]
    selected_models = [v.lower() for v in get_list('model')]
    selected_auctions = [v.lower() for v in get_list('auction')]
    selected_buy_now = [v.lower() for v in get_list('buy_now')]
    selected_locations = [v.lower() for v in get_list('location')]
    selected_buyer_countries = [v.lower() for v in get_list('buyer_country')]

    make = request.GET.get('make')
    if make:
        make = make.strip().lower()
        if make == "all makes":
            make = None

    model = request.GET.get('model')
    if model:
        model = model.strip().lower()
        if model == "all models":
            model = None

    auction = request.GET.get('auction')
    if auction:
        auction = auction.strip().lower()
        if auction == "all auctions":
            auction = None

    from_year = request.GET.get('from_year')
    to_year = request.GET.get('to_year')
    sale_date_from = request.GET.get('sale_date_from')
    sale_date_to = request.GET.get('sale_date_to')
    min_odometer = request.GET.get('min_odometer')
    max_odometer = request.GET.get('max_odometer')

    odometer_range = request.GET.get('odometer_range')
    if odometer_range:
        parts = odometer_range.split('-')
        min_odometer = parts[0] if parts[0] else ''
        max_odometer = parts[1] if len(parts) > 1 and parts[1] else ''

    if auction:
        vehicles_qs = vehicles_qs.extra(where=["LOWER(auction_name) = %s"], params=[auction])

    if buyer_country:
        for country in buyer_country:
            vehicles_qs = vehicles_qs.filter(sales_history__icontains=f'"buyer_country": "{country}"')

    try:
        sale_date_from = datetime.strptime(sale_date_from, '%Y-%m-%d').date() if sale_date_from else None
    except ValueError:
        sale_date_from = None

    try:
        sale_date_to = datetime.strptime(sale_date_to, '%Y-%m-%d').date() if sale_date_to else None
    except ValueError:
        sale_date_to = None

    if make:
        vehicles_qs = vehicles_qs.annotate(make_lower=Lower('make')).filter(make_lower=make)
    if model:
        vehicles_qs = vehicles_qs.annotate(model_lower=Lower('model')).filter(model_lower=model)
    if auction:
        vehicles_qs = vehicles_qs.annotate(auction_name_lower=Lower('auction_name')).filter(auction_name_lower=auction)
    if damage:
        vehicles_qs = vehicles_qs.annotate(primary_damage_lower=Lower('primary_damage')).filter(primary_damage_lower=damage)
    if engine_type:
        vehicles_qs = vehicles_qs.annotate(engine_type_lower=Lower('engine_type')).filter(engine_type_lower__in=engine_type)

    if from_year and from_year.isdigit():
        vehicles_qs = vehicles_qs.filter(year__gte=int(from_year))
    if to_year and to_year.isdigit():
        vehicles_qs = vehicles_qs.filter(year__lte=int(to_year))
    if min_odometer:
        vehicles_qs = vehicles_qs.filter(odometer__gte=float(min_odometer))
    if max_odometer:
        vehicles_qs = vehicles_qs.filter(odometer__lte=float(max_odometer))
    if location:
        vehicles_qs = vehicles_qs.annotate(location_lower=Lower('location')).filter(location_lower__in=location)

    for field, values in [
        ('engine_type', engine_type),
        ('location', location),
        ('fuel', fuel_type),
        ('color', color),
        ('primary_damage', primary_damage),
        ('secondary_damage', secondary_damage),
        ('transmission', transmission),
        ('cylinders', cylinders),
        ('body_style', body_style),
        ('vehicle_type', selected_vehicle_types),
        ('seller', seller),
        ('drive', driveline),
    ]:
        if values:
            in_tuple = tuple(values)
            if len(in_tuple) == 1:
                vehicles_qs = vehicles_qs.extra(where=[f"LOWER({field}) = %s"], params=[in_tuple[0]])
            else:
                vehicles_qs = vehicles_qs.extra(where=[f"LOWER({field}) IN %s"], params=[in_tuple])

    if buy_now:
        show_yes = 'yes' in buy_now
        show_no = 'no' in buy_now
        if show_yes and not show_no:
            vehicles_qs = vehicles_qs.exclude(
                Q(buy_now_car__isnull=True) |
                Q(buy_now_car__exact='') |
                Q(buy_now_car__exact='null') |
                Q(buy_now_car__exact='{}')
            )
        elif show_no and not show_yes:
            vehicles_qs = vehicles_qs.filter(
                Q(buy_now_car__isnull=True) |
                Q(buy_now_car__exact='') |
                Q(buy_now_car__exact='null') |
                Q(buy_now_car__exact='{}')
            )

    paginator = Paginator(vehicles_qs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # vehicles = page_obj.object_list
    vehicles = list(page_obj.object_list)

    for v in vehicles:
        v.final_bid = 0
        v.latest_sale_date = None
        v.latest_purchase_price = 0
        v.buyer_country = 'N/A'
        try:
            sales_history = json.loads(v.sales_history) if isinstance(v.sales_history, str) else v.sales_history or []
        except Exception:
            sales_history = []
        if sales_history:
            latest_sale = sales_history[-1]
            sale_timestamp = latest_sale.get('sale_date')
            try:
                v.latest_sale_date = datetime.utcfromtimestamp(sale_timestamp).date() if isinstance(sale_timestamp, int) else datetime.strptime(sale_timestamp, '%Y-%m-%d').date()
            except Exception:
                v.latest_sale_date = None
            v.latest_purchase_price = latest_sale.get('purchase_price', 0)
            v.buyer_country = latest_sale.get('buyer_country', 'N/A')
        try:
            sales_history = json.loads(v.sales_history) if isinstance(v.sales_history, str) else v.sales_history or []
        except Exception:
            sales_history = []
        if isinstance(sales_history, list) and sales_history:
            latest_sale = sales_history[-1]
            v.sale_status = latest_sale.get('sale_status', '')
        active = v.active_bidding
        bid_val = active.get('current_bid', 0) if isinstance(active, dict) else 0
        if isinstance(bid_val, str):
            bid_val = re.sub(r'[^\d.]', '', bid_val)
        try:
            v.final_bid = float(bid_val)
        except Exception:
            v.final_bid = 0
        raw_photos = v.car_photo_urls
        car_photos = [url.strip().strip('"') for url in raw_photos.strip('{}').split(',') if url.strip()] if isinstance(raw_photos, str) else raw_photos or []
        v.car_photos = car_photos
        v.primary_photo = car_photos[0] if car_photos else ''

           # Apply 'newly added' and 'sale_status' filters
    if newly_added:
        temp = []
        for v in vehicles:
            created = v.created_at.date() if v.created_at else ''
            if '24h' in newly_added and created and created >= (now - timedelta(days=1)).date():
                temp.append(v)
            elif '7d' in newly_added and created and created >= (now - timedelta(days=7)).date():
                temp.append(v)
        vehicles = temp

    if sale_status_filter:
        sale_status_filter_lower = [s.lower() for s in sale_status_filter]
        vehicles = [v for v in vehicles if v.sale_status.lower() in sale_status_filter_lower]

    # Sorting
    if sort_field == 'sale_date':
        vehicles.sort(key=lambda x: x.latest_sale_date or datetime.min.date(), reverse=(sort_order == 'desc'))
    elif sort_field == 'final_bid':
        vehicles.sort(key=lambda x: x.latest_purchase_price or 0, reverse=(sort_order == 'desc'))
    else:
        vehicles.sort(key=lambda x: x.created_at, reverse=True)

    # Filter by actual auction sale date
    if sale_date_from or sale_date_to:
        filtered_vehicles = []
        for v in vehicles:
            if v.latest_sale_date:
                if sale_date_from and sale_date_to:
                    if sale_date_from <= v.latest_sale_date <= sale_date_to:
                        filtered_vehicles.append(v)
                elif sale_date_from and not sale_date_to:
                    if v.latest_sale_date >= sale_date_from:
                        filtered_vehicles.append(v)
                elif not sale_date_from and sale_date_to:
                    if v.latest_sale_date <= sale_date_to:
                        filtered_vehicles.append(v)
        vehicles = filtered_vehicles

    # Refined queryset for dropdowns and counts
    # refined_ids = [v.id for v in vehicles]
    # refined_queryset = Vehicle.objects.filter(id__in=refined_ids)
    refined_queryset = vehicles_qs  # use the full filtered queryset before pagination


    sale_dates = sorted(set(v.latest_sale_date for v in vehicles if v.latest_sale_date), reverse=True)
    newly_added_24h_count = Vehicle.objects.filter(to_be_published=True, created_at__gte=(now - timedelta(days=1))).count()
    newly_added_7d_count = Vehicle.objects.filter(to_be_published=True, created_at__gte=(now - timedelta(days=7))).count()

    country_counter = defaultdict(int)
    for raw in refined_queryset.values_list('sales_history', flat=True):
        try:
            sales_list = raw if isinstance(raw, list) else json.loads(raw or "[]")
            for sale in sales_list:
                if isinstance(sale, dict):
                    country = sale.get("buyer_country")
                    if country:
                        country_counter[country.strip().title()] += 1
        except Exception:
            pass
    buyer_countries_list = [{'field': k, 'count': v} for k, v in country_counter.items()]

    # Dropdowns
    makes = get_field_counts(refined_queryset, 'make')
    models_queryset = refined_queryset.extra(where=["LOWER(make) = %s"], params=[make]) if make else refined_queryset
    models = get_field_counts(models_queryset, 'model')
    years_queryset = models_queryset.extra(where=["LOWER(model) = %s"], params=[model]) if model and make else models_queryset
    years = sorted(get_field_counts(years_queryset, 'year'), key=lambda x: x['year'])

    get_params = request.GET.copy()
    get_params.pop('page', None)
    get_params.pop('sort', None)
    get_params.pop('order', None)
    querystring = get_params.urlencode()

    location_counts = refined_queryset.values('location').annotate(count=Count('id')).order_by('-count')

    context = {
        'selected_auctions': selected_auctions,
        'selected_locations': selected_locations,
        'selected_buyer_countries': selected_buyer_countries,
        'newly_added_24h_count': newly_added_24h_count,
        'newly_added_7d_count': newly_added_7d_count,
        'querystring': querystring,
        'page_obj': page_obj,
        'vehicles': vehicles,  # Already paginated and enriched
        'total_vehicles': paginator.count,
        'auctions': get_field_counts(Vehicle.objects.filter(to_be_published=True), 'auction_name'),
        'fuel_types': get_field_counts(refined_queryset, 'fuel'),
        'engine_types': get_field_counts(refined_queryset, 'engine_type'),
        'primary_damages': get_field_counts(refined_queryset, 'primary_damage'),
        'secondary_damages': get_field_counts(refined_queryset, 'secondary_damage'),
        'transmissions': get_field_counts(refined_queryset, 'transmission'),
        'vehicle_types': get_field_counts(refined_queryset, 'vehicle_type'),
        'body_styles': get_field_counts(refined_queryset, 'body_style'),
        'cylinders': get_field_counts(refined_queryset, 'cylinders'),
        'colors': get_field_counts(refined_queryset, 'color'),
        'buy_now_options': get_buy_now_options(refined_queryset),
        'sale_status_counts': {
            'Sold': sum(1 for v in vehicles if v.sale_status.lower() == 'sold'),
            'Not sold': sum(1 for v in vehicles if v.sale_status.lower() == 'not sold'),
        },
        'locations_with_counts': location_counts,
        'buyer_countries': buyer_countries_list,
        'newly_added': newly_added,
        'sale_date_from': sale_date_from,
        'sale_date_to': sale_date_to,
        'sale_status': sale_status_filter,
        'locations': location,
        'from_year': from_year,
        'to_year': to_year,
        'min_odometer': min_odometer,
        'max_odometer': max_odometer,
        'selected_engine_type': engine_type,
        'selected_fuel_type': fuel_type,
        'selected_color': color,
        'selected_primary_damage': primary_damage,
        'selected_secondary_damage': secondary_damage,
        'selected_cylinders': cylinders,
        'selected_body_style': body_style,
        'selected_seller': seller,
        'buy_now': buy_now,
        'selected_buy_now': selected_buy_now,
        'selected_driveline': driveline,
        'sale_dates': sale_dates,
        'makes': makes,
        'make': make.title() if make else None,
        'models': models,
        'model': model.title() if model else None,
        'selected_models': selected_models,
        'years': years,
        'selected_vehicle_type': selected_vehicle_types,
        'selected_transmission': transmission,
    }

    return render(request, 'search.html', context)


def car_details(request, id):
    try:
        car_id = int(id)
    except ValueError:
        raise Http404("Invalid vehicle ID.")

    vehicle = get_object_or_404(Vehicle, pk=car_id, to_be_published=True)

    # Handling car photo URLs
    raw_photos = vehicle.car_photo_urls
    if isinstance(raw_photos, str):
        car_photos = [url.strip().strip('"') for url in raw_photos.strip('{}').split(',') if url.strip()]
    elif isinstance(raw_photos, list):
        car_photos = raw_photos
    else:
        car_photos = []

    vehicle_images_length = len(car_photos)

    # Handling buy now prices
    buy_now_prices = []
    raw_buy_now = vehicle.buy_now_price_histories
    if isinstance(raw_buy_now, str):
        try:
            buy_now_prices = json.loads(raw_buy_now)
        except json.JSONDecodeError:
            buy_now_prices = []
    elif isinstance(raw_buy_now, dict):
        buy_now_prices = raw_buy_now.get('history', [])
    elif isinstance(raw_buy_now, list):
        buy_now_prices = raw_buy_now

    print("price", buy_now_prices)

    if buy_now_prices != 0:
        for price in buy_now_prices:
            if isinstance(price.get('start_date'), int):
                price['start_date'] = datetime.utcfromtimestamp(price['start_date']).strftime('%Y-%m-%d')



    # Handling sales history (no processing, raw data)
    raw_sales = vehicle.sales_history

    # Check if raw_sales is a string or a list of sales entries
    sales_history = []
    if isinstance(raw_sales, str):
        try:
            sales_history = json.loads(raw_sales)
        except Exception:
            sales_history = []
    elif isinstance(raw_sales, list):
        sales_history = raw_sales

    # Process sales data (convert sale date from timestamp)
    for sale in sales_history:
        if isinstance(sale, dict):
            if isinstance(sale.get('sale_date'), int):
                sale['sale_date'] = datetime.utcfromtimestamp(sale['sale_date']).strftime('%Y-%m-%d')
            elif not isinstance(sale.get('sale_date'), str):
                sale['sale_date'] = 'Not Available'

            auction_info = sale.get('auction_info')
            if isinstance(auction_info, dict):
                sale['country_name'] = auction_info.get('country_name', 'Not Available')
            else:
                sale['country_name'] = 'Not Available'

    # Removing duplicates based on lot_number and sale_date
    unique_sales = []
    seen = set()
    for sale in sales_history:
        sale_key = f"{sale.get('lot_number')}-{sale.get('sale_date')}"
        if sale_key not in seen:
            seen.add(sale_key)
            unique_sales.append(sale)

    # Sorting sales history by sale date
    def sale_date_key(x):
        try:
            return datetime.strptime(x['sale_date'], "%Y-%m-%d")
        except Exception:
            return datetime.min

    unique_sales = sorted(unique_sales, key=sale_date_key, reverse=True)

    # Get the latest sale
    latest_sale = unique_sales[0] if unique_sales else {}
    latest_sale.setdefault('sale_status', 'Not Available')
    latest_sale.setdefault('purchase_price', 'Not Available')

    # Collect all sale dates for further processing
    sale_dates = []
    for sale in unique_sales:
        if isinstance(sale, dict):
            date = sale.get('sale_date')
            if date:
                sale_dates.append(date)

    # Parse sale dates to datetime objects for comparison
    parsed_dates = []
    for d in sale_dates:
        try:
            parsed_dates.append(datetime.strptime(d, "%Y-%m-%d").date())
        except Exception:
            pass

    # Find the latest sale date
    latest_sale_date = max(parsed_dates) if parsed_dates else None

    print({
                'vehicle': vehicle.__dict__,
        'latest_sale': latest_sale,
        'sales_history': unique_sales,  # Pass the unique sales history to the template
        'buy_now_prices': buy_now_prices,
        'vin_record': vehicle,
        'vehicle_images_length': vehicle_images_length,
        'vin_image_index_start': vehicle_images_length,
        'photo_urls': car_photos,
        'latest_sale_date': latest_sale_date
    })

    # Returning the data to render the template
    return render(request, 'auction-car-details.html', {
        'vehicle': vehicle,
        'latest_sale': latest_sale,
        'sales_history': unique_sales,  # Pass the unique sales history to the template
        'buy_now_prices': buy_now_prices,
        'vin_record': vehicle,
        'vehicle_images_length': vehicle_images_length,
        'vin_image_index_start': vehicle_images_length,
        'photo_urls': car_photos,
        'latest_sale_date': latest_sale_date
    })

def get_models_by_make(request):
    make = request.GET.get('make')
    # Fetch models for the selected make (case-insensitive)
    models = Vehicle.objects.filter(make__iexact=make).values_list('model', flat=True).distinct()
    return JsonResponse({'models': list(models)})


def vehicle_search_api(request):
    query = request.GET.get('q', '').strip().lower()
    results = []

    if query:
        vehicles = Vehicle.objects.filter(
            Q(vin__icontains=query) | Q(lot_number__icontains=query)
        )

        for vehicle in vehicles:
            results.append({
                'id': vehicle.id,
                'vin': vehicle.vin,
                'lot_number': vehicle.lot_number,
                'year': vehicle.year,
                'make': vehicle.make,
                'model': vehicle.model,
            })

    return JsonResponse({'vehicles': results})


@csrf_exempt
def vechile_api_manual_form(request):
    api_token = '6394dc91ece3542af402645dc9f2aa1b2c2dec923b24cf3d249373228a019684'   

    if request.method == 'POST':
        filters = {
            'make': request.POST.get('make', ''),
            'model': request.POST.get('model', ''),
            'year_from': request.POST.get('year_from', ''),
            'year_to': request.POST.get('year_to', ''),
            'auction_name': request.POST.get('auction_name', ''),
            'auction_date_from': request.POST.get('auction_date_from', ''),
            'auction_date_to': request.POST.get('auction_date_to', ''),
            'sale_price_from': request.POST.get('sale_price_from', ''),
            'sale_price_to': request.POST.get('sale_price_to', ''),
            'is_buy_now': request.POST.get('is_buy_now', ''),
            'odometer_from': request.POST.get('odometer_from', ''),
            'odometer_to': request.POST.get('odometer_to', ''),
            'updated_at_from': request.POST.get('updated_at_from', ''),
            'updated_at_to': request.POST.get('updated_at_to', ''),
            'estimate_retail_from': request.POST.get('estimate_retail_from', ''),
            'estimate_retail_to': request.POST.get('estimate_retail_to', ''),
            'created_at_from': request.POST.get('created_at_from', ''),
            'created_at_to': request.POST.get('created_at_to', ''),
            'car_info_vehicle_type': request.POST.get('car_info_vehicle_type', ''),
            'per_page': 50,
            'page': request.POST.get('page', ''),
        }
        obj, _ = SuperuserLastSearch.objects.get_or_create(id=1)
        obj.filters = filters
        obj.save()
        cancel_check = lambda: SuperuserLastSearch.objects.get(id=1).job_cancelled

        current_page = int(filters['page'])
        per_page = int(filters['per_page'])
        total_pages = None

        def safe_str(value):
            if isinstance(value, str):
                return value[:100]
            elif value is None:
                return ''
            else:
                return str(value)[:100]
        pages_saved = []

        try:
            while total_pages is None or current_page <= total_pages:
                
                print(f"[INFO] Fetching page {current_page}...")
               
                if cancel_check():
                    print("[CANCELLED] Job stopped by user.")
                    break
            
                api_url = f"https://copart-iaai-api.com/api/v2/get-cars?api_token={api_token}&page={current_page}&per_page={per_page}"

                headers = {'Content-Type': 'application/json'}
                body = {k: v for k, v in filters.items() if k not in ['page', 'per_page'] and v not in [None, '', 'null']}
                # data = fetch_data_with_retry_manuall(api_url, body, headers)

                
                try:
                    response = requests.post(api_url, headers=headers, json=body, timeout=5)
                    response.raise_for_status()
                    data = response.json()
                except Exception as e:
                    print(f"[ERROR] API request failed on page {current_page}: {str(e)}")
                    break

                total_pages = int(data['pagination']['total_pages'])
                results = data.get('result', [])
                print(f"[INFO] Received {len(results)} vehicles on page {current_page}")              

                for v in results:
                    car_info_data = v.get('car_info', {})
                    car_info_obj = None

                    if isinstance(car_info_data, dict):
                        car_info_obj, _ = CarInfo.objects.update_or_create(
                            all_lots_id=car_info_data.get('all_lots_id'),
                            defaults={
                                'make': safe_str(car_info_data.get('make', {}).get('make')),
                                'model': safe_str(car_info_data.get('model', {}).get('model')),
                                'series': safe_str(car_info_data.get('series', {}).get('series')),
                                'vehicle_type': safe_str(car_info_data.get('vehicle_type', {}).get('vehicle_type')),
                                'body_class': safe_str(car_info_data.get('body_class', {}).get('body_class')),
                                'make_id': car_info_data.get('make_id') or 0,
                                'model_id': car_info_data.get('model_id') or 0,
                                'series_id': car_info_data.get('series_id') or 0,
                                'vehicle_type_id': car_info_data.get('vehicle_type_id') or 0,
                                'body_class_id': car_info_data.get('body_class_id') or 0,
                            }
                        )

                    # Check if vehicle exists by vin
                    vehicle_obj = Vehicle.objects.filter(vin=v.get('vin')).first()

                    if vehicle_obj:
                        # If VIN exists, only update if fields are different (e.g., `updated_at`)
                        if vehicle_obj.updated_at != v.get('updated_at'):
                            vehicle_obj.updated_at = v.get('updated_at')
                            vehicle_obj.save(update_fields=["updated_at"])
                            print(f"[UPDATED] VIN: {v.get('vin')} updated.")
                    else:
                        # If VIN does not exist, create a new record
                        Vehicle.objects.create(
                            vin=v.get('vin'),
                            lot_id=v.get('id'),
                            auction_name=safe_str(v.get('auction_name')),
                            make=safe_str(v.get('make')),
                            model=safe_str(v.get('model')),
                            year=v.get('year'),
                            body_style=v.get('body_style'),
                            car_keys=v.get('car_keys'),
                            color=v.get('color'),
                            cylinders=v.get('cylinders'),
                            doc_type=v.get('doc_type'),
                            drive=v.get('drive'),
                            engine_type=v.get('engine_type'),
                            est_retail_value=v.get('est_retail_value'),
                            fuel=v.get('fuel'),
                            highlights=v.get('highlights'),
                            location=v.get('location'),
                            lot_number=v.get('lot_number'),
                            odometer=v.get('odometer'),
                            primary_damage=v.get('primary_damage'),
                            secondary_damage=v.get('secondary_damage'),
                            seller=v.get('seller'),
                            series=v.get('series'),
                            transmission=v.get('transmission'),
                            vehicle_type=v.get('vehicle_type'),
                            is_insurance=v.get('is_insurance'),
                            currency_name=v.get('currency', {}).get('name'),
                            currency_code=v.get('currency', {}).get('char_code'),
                            car_photo_urls=v.get('car_photo', {}).get('photo', []),
                            damage_photos=v.get('damage_photos', []),
                            buy_now_price_histories=v.get('buy_now_price_histories', []),
                            sales_history=v.get('sales_history', []),
                            active_bidding=v.get('active_bidding', []),
                            buy_now_car=v.get('buy_now_car', {}),
                            car_info=car_info_obj,
                            updated_at=None,
                            created_at=timezone.now(),
                        )
                        print(f"[CREATED] VIN: {v.get('vin')} created.")

                pages_saved.append(current_page)
                print(f"[SAVED] ✅ Page {current_page} saved with {len(results)} vehicles.")

                request.session['fetch_progress'] = {
                    "current_page": current_page
                }
                request.session.modified = True
                obj.filters['page'] = current_page
                obj.save()
                current_page += 1  
                time.sleep(1)

        except Exception as e:
            print(f"[FATAL ERROR] Unexpected error occurred: {str(e)}")
        finally:
            print("[VIN FETCH] ⏳ Starting VIN fetch...")
            # fetch_car_vin_data()
            print("[VIN FETCH] ✅ VIN fetch complete.")       
        print(f"[COMPLETE] ✅ All pages processed up to page {current_page - 1}.")

        return JsonResponse({
            "message": f"Fetched and saved page {current_page}",
            "pagination": {
                "current_page": current_page,
                "total_pages": total_pages,
                "results_saved": len(results),
                "start_page": int(filters['page']),
                "end_page": current_page - 1,
                "total_saved": len(pages_saved),
                "pages_saved": pages_saved,
                "next_page": current_page 
            }
        })

    else:
        try:
            last_search = SuperuserLastSearch.objects.get(id=1)
            saved_filters = last_search.filters
        except SuperuserLastSearch.DoesNotExist:
            saved_filters = {}

        return render(request, 'vehicle-manual-form.html', {
            'saved_filters': saved_filters,
            'api_token': api_token
        })



def handle_null_values(data):
    # Check if data is a string and equals to "null" or curly quotes versions
    if isinstance(data, str):
        data = data.strip()  # Remove any surrounding whitespace
        if data.lower() in ["null", "“null”", "”null“"]:
            return None
    return data

@csrf_exempt
def vechile_get_vin_manual_form(request):
    if request.method == 'POST':
        # Get data from request
        api_token = request.POST.get('api_token', default_token)
        vin = request.POST.get('vin')
        only_with_color = request.POST.get('is_buy_now', '0')
        
        # Check if VIN is provided
        if not vin:
            return JsonResponse({"error": "VIN is required."}, status=400)

        # Check if the vehicle exists with the given VIN
        vehicle = Vehicle.objects.filter(vin=vin).first()

        if not vehicle:
            return JsonResponse({"error": f"No vehicle found with VIN {vin}."}, status=404)

        # Build query params
        params = {
            "api_token": api_token,
            "vin_number": vin,
            "only_with_color": only_with_color
        }

        try:
            response = requests.post(
            "https://copart-iaai-api.com/api/v1/get-car-vin",
            params=params,
            headers=HEADERS,
            data='',
            timeout=60 
        )
#             response= {
#   "result": [
#     {
#       "id": 11244703,
#       "auction_name": "IAAI",
#       "body_style": "Utility",
#       "car_keys": "no",
#       "color": "Black",
#       "cylinders": "6 Cylinders",
#       "doc_type": None,
#       "drive": "All Wheel Drive",
#       "engine_type": "3.8L DOHC V6 W/DUAL CVVT",
#       "est_retail_value": 44964,
#       "fuel": "Gasoline",
#       "highlights": "Stationary",
#       "location": "Newburgh (NY)",
#       "lot_number": 32639985,
#       "make": "KIA",
#       "model": "TELLURIDE",
#       "odometer": 12355,
#       "primary_damage": "Right Side",
#       "secondary_damage": "All Over",
#       "seller": " Geico Insurance",
#       "series": "EX",
#       "transmission": "Automatic Transmission",
#       "vehicle_type": "AUTOMOBILE",
#       "vin": "5XYP3DHC1NG225508",
#       "year": 2022,
#       "is_insurance": None,
#       "currency_code_id": 1,
#       "created_at": "2023-01-12 15:10:05",
#       "damage_photos": [],
#       "car_photo": {
#         "id": 7489376,
#         "all_lots_id": 11244703,
#         "photo": [
#           "https://anvis.iaai.com/resizer?imageKeys=33108918~SID~B635~S0~I1~RW2592~H1944~TH0&width=845&height=633",
#           "https://anvis.iaai.com/resizer?imageKeys=33108918~SID~B635~S0~I2~RW2592~H1944~TH0&width=845&height=633",
#           "https://anvis.iaai.com/resizer?imageKeys=33108918~SID~B635~S0~I3~RW2592~H1944~TH0&width=845&height=633",
#           "https://anvis.iaai.com/resizer?imageKeys=33108918~SID~B635~S0~I4~RW2592~H1944~TH0&width=845&height=633",
#           "https://anvis.iaai.com/resizer?imageKeys=33108918~SID~B635~S0~I5~RW2592~H1944~TH0&width=845&height=633",
#           "https://anvis.iaai.com/resizer?imageKeys=33108918~SID~B635~S0~I6~RW2592~H1944~TH0&width=845&height=633",
#           "https://anvis.iaai.com/resizer?imageKeys=33108918~SID~B635~S0~I7~RW2592~H1944~TH0&width=845&height=633",
#           "https://anvis.iaai.com/resizer?imageKeys=33108918~SID~B635~S0~I8~RW2592~H1944~TH0&width=845&height=633",
#           "https://anvis.iaai.com/resizer?imageKeys=33108918~SID~B635~S0~I9~RW2592~H1944~TH0&width=845&height=633",
#           "https://anvis.iaai.com/resizer?imageKeys=33108918~SID~B635~S0~I10~RW2592~H1944~TH0&width=845&height=633"
#         ]
#       },
#       "car_info": {
#         "id": 10040011,
#         "all_lots_id": 11244703,
#         "make_id": 23,
#         "model_id": 724,
#         "series_id": 26011,
#         "vehicle_type_id": 2,
#         "body_class_id": 3,
#         "make": {
#           "id": 23,
#           "make": "KIA",
#           "make_slug": "kia",
#           "created_at": "2023-03-16 12:49:36",
#           "updated_at": "2023-03-16 10:50:37"
#         },
#         "model": {
#           "id": 724,
#           "model": "TELLURIDE",
#           "model_slug": "telluride",
#           "make_id": 23,
#           "created_at": "2023-03-16 12:50:14",
#           "updated_at": "2023-03-16 10:55:20"
#         },
#         "series": {
#           "id": 26011,
#           "series": "EX",
#           "model_id": 724
#         },
#         "vehicle_type": {
#           "id": 2,
#           "vehicle_type": "MULTIPURPOSE PASSENGER VEHICLE (MPV)"
#         },
#         "body_class": {
#           "id": 3,
#           "body_class": "SPORT UTILITY VEHICLE (SUV)/MULTI-PURPOSE VEHICLE (MPV)"
#         }
#       },
#       "sales_history": [
#         {
#           "id": 22414080,
#           "all_lots_id": 11244703,
#           "auction": 1,
#           "lot_number": 32639985,
#           "purchase_price": 18300,
#           "sale_status": "Sold",
#           "sold": 1,
#           "buyer_id": None,
#           "buyer_state": None,
#           "buyer_country": None,
#           "sale_date": 1659533400,
#           "auction_info": {
#             "auction_code": 1,
#             "country_name": "United States"
#           }
#         }
#       ],
#       "active_bidding": [],
#       "buy_now_car": None,
#       "currency": {
#         "id": 1,
#         "name": "US Dollar",
#         "char_code": "USD",
#         "iso_code": 840,
#         "code_id": 1
#       },
#       "buy_now_price_histories": []
#     },
#     {
#       "id": 48326564,
#       "auction_name": "COPART",
#       "body_style": None,
#       "car_keys": "yes",
#       "color": "BLACK",
#       "cylinders": "6",
#       "doc_type": None,
#       "drive": "All wheel drive",
#       "engine_type": "3.8L  6",
#       "est_retail_value": 57959,
#       "fuel": "GAS",
#       "highlights": "RUNS AND DRIVES",
#       "location": "NY - NEWBURGH",
#       "lot_number": 38703173,
#       "make": "KIA",
#       "model": "TELLURIDE",
#       "odometer": 13094,
#       "primary_damage": "MINOR DENT/SCRATCHES",
#       "secondary_damage": None,
#       "seller": None,
#       "series": None,
#       "transmission": "AUTOMATIC",
#       "vehicle_type": "AUTOMOBILE",
#       "vin": "5XYP3DHC1NG225508",
#       "year": 2022,
#       "is_insurance": None,
#       "currency_code_id": 1,
#       "created_at": "2023-01-25 12:17:00",
#       "damage_photos": [],
#       "car_photo": {
#         "id": 15265523,
#         "all_lots_id": 48326564,
#         "photo": [
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/LPP542/7a76b7ced6a1458693db1f2af4abd8c2_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/LPP542/542af709ff82466d8dfef398e917f5b4_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/LPP542/3a702e7deb2b47d09d109bae14cb6e75_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/LPP542/4337fe47812c4c31a7edac717d9d6621_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/LPP542/fad86b642230429e8ce80f0dcb341ce2_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/LPP542/1c51ba42f1c64a53bf0036e89aceef8d_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/LPP542/294286f0e6b34d3ebd45fcaf2253b280_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/LPP542/2d939c59adc345c1ae4cc4c82fb43bed_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/LPP542/20c0fa713faa4718b840e23eaee9fb5f_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/LPP542/6046c6ffc4f94f548d08c04a6b4ca640_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/LPP542/24ba33c414ff496da30c32ed2758a3c8_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/LPP542/4fc710c60b6a4ac3bfaf073bf638f0f1_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/LPP542/7975394bdb514cadbf7a5fa8aca51f19_ful.jpg"
#         ]
#       },
#       "car_info": {
#         "id": 14800352,
#         "all_lots_id": 48326564,
#         "make_id": 23,
#         "model_id": 724,
#         "series_id": 26011,
#         "vehicle_type_id": 2,
#         "body_class_id": 3,
#         "make": {
#           "id": 23,
#           "make": "KIA",
#           "make_slug": "kia",
#           "created_at": "2023-03-16 12:49:36",
#           "updated_at": "2023-03-16 10:50:37"
#         },
#         "model": {
#           "id": 724,
#           "model": "TELLURIDE",
#           "model_slug": "telluride",
#           "make_id": 23,
#           "created_at": "2023-03-16 12:50:14",
#           "updated_at": "2023-03-16 10:55:20"
#         },
#         "series": {
#           "id": 26011,
#           "series": "EX",
#           "model_id": 724
#         },
#         "vehicle_type": {
#           "id": 2,
#           "vehicle_type": "MULTIPURPOSE PASSENGER VEHICLE (MPV)"
#         },
#         "body_class": {
#           "id": 3,
#           "body_class": "SPORT UTILITY VEHICLE (SUV)/MULTI-PURPOSE VEHICLE (MPV)"
#         }
#       },
#       "sales_history": [
#         {
#           "id": 29138735,
#           "all_lots_id": 48326564,
#           "auction": 2,
#           "lot_number": 38703173,
#           "purchase_price": 19100,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 268100,
#           "buyer_state": "AR",
#           "buyer_country": "USA",
#           "sale_date": 1675177200,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 29262332,
#           "all_lots_id": 48326564,
#           "auction": 2,
#           "lot_number": 38703173,
#           "purchase_price": 19200,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 159113,
#           "buyer_state": "NJ",
#           "buyer_country": "USA",
#           "sale_date": 1675389600,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 29387225,
#           "all_lots_id": 48326564,
#           "auction": 2,
#           "lot_number": 38703173,
#           "purchase_price": 12200,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 268100,
#           "buyer_state": "AR",
#           "buyer_country": "USA",
#           "sale_date": 1675782000,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 29532020,
#           "all_lots_id": 48326564,
#           "auction": 2,
#           "lot_number": 38703173,
#           "purchase_price": 14100,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 159113,
#           "buyer_state": "NJ",
#           "buyer_country": "USA",
#           "sale_date": 1675994400,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 29649649,
#           "all_lots_id": 48326564,
#           "auction": 2,
#           "lot_number": 38703173,
#           "purchase_price": 17000,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 500937,
#           "buyer_state": "FL",
#           "buyer_country": "USA",
#           "sale_date": 1676386800,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 29807867,
#           "all_lots_id": 48326564,
#           "auction": 2,
#           "lot_number": 38703173,
#           "purchase_price": 18000,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 680880,
#           "buyer_state": "CA",
#           "buyer_country": "USA",
#           "sale_date": 1676599200,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 29911013,
#           "all_lots_id": 48326564,
#           "auction": 2,
#           "lot_number": 38703173,
#           "purchase_price": 16300,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 268100,
#           "buyer_state": "AR",
#           "buyer_country": "USA",
#           "sale_date": 1676991600,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 30093738,
#           "all_lots_id": 48326564,
#           "auction": 2,
#           "lot_number": 38703173,
#           "purchase_price": 16400,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 358076,
#           "buyer_state": "CA",
#           "buyer_country": "USA",
#           "sale_date": 1677204000,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 30193372,
#           "all_lots_id": 48326564,
#           "auction": 2,
#           "lot_number": 38703173,
#           "purchase_price": 6300,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 268100,
#           "buyer_state": "AR",
#           "buyer_country": "USA",
#           "sale_date": 1677596400,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 30367965,
#           "all_lots_id": 48326564,
#           "auction": 2,
#           "lot_number": 38703173,
#           "purchase_price": 13000,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 268100,
#           "buyer_state": "AR",
#           "buyer_country": "USA",
#           "sale_date": 1677808800,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 30504941,
#           "all_lots_id": 48326564,
#           "auction": 2,
#           "lot_number": 38703173,
#           "purchase_price": 10100,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 125026,
#           "buyer_state": "UE",
#           "buyer_country": "ARE",
#           "sale_date": 1678201200,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 30648920,
#           "all_lots_id": 48326564,
#           "auction": 2,
#           "lot_number": 38703173,
#           "purchase_price": 12600,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 268100,
#           "buyer_state": "AR",
#           "buyer_country": "USA",
#           "sale_date": 1678413600,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 30749585,
#           "all_lots_id": 48326564,
#           "auction": 2,
#           "lot_number": 38703173,
#           "purchase_price": 9100,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 638766,
#           "buyer_state": "TX",
#           "buyer_country": "USA",
#           "sale_date": 1678802400,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 30926643,
#           "all_lots_id": 48326564,
#           "auction": 2,
#           "lot_number": 38703173,
#           "purchase_price": 15100,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 268100,
#           "buyer_state": "AR",
#           "buyer_country": "USA",
#           "sale_date": 1679014800,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 31025497,
#           "all_lots_id": 48326564,
#           "auction": 2,
#           "lot_number": 38703173,
#           "purchase_price": 18200,
#           "sale_status": "Sold",
#           "sold": 1,
#           "buyer_id": 268100,
#           "buyer_state": "AR",
#           "buyer_country": "USA",
#           "sale_date": 1679407200,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         }
#       ],
#       "active_bidding": [],
#       "buy_now_car": None,
#       "currency": {
#         "id": 1,
#         "name": "US Dollar",
#         "char_code": "USD",
#         "iso_code": 840,
#         "code_id": 1
#       },
#       "buy_now_price_histories": [
#         {
#           "id": 34391593,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 24500,
#           "start_date": "2023-03-21"
#         },
#         {
#           "id": 34372452,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 24500,
#           "start_date": "2023-03-20"
#         },
#         {
#           "id": 34179115,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 24500,
#           "start_date": "2023-03-17"
#         },
#         {
#           "id": 34142149,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 24500,
#           "start_date": "2023-03-16"
#         },
#         {
#           "id": 34118153,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 24500,
#           "start_date": "2023-03-15"
#         },
#         {
#           "id": 33744250,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 24500,
#           "start_date": "2023-03-10"
#         },
#         {
#           "id": 33693997,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 24500,
#           "start_date": "2023-03-09"
#         },
#         {
#           "id": 32986658,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 23500,
#           "start_date": "2023-02-24"
#         },
#         {
#           "id": 32945307,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 23500,
#           "start_date": "2023-02-23"
#         },
#         {
#           "id": 32907380,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 23500,
#           "start_date": "2023-02-22"
#         },
#         {
#           "id": 32763613,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 23500,
#           "start_date": "2023-02-21"
#         },
#         {
#           "id": 32725346,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 23500,
#           "start_date": "2023-02-20"
#         },
#         {
#           "id": 32654419,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 23500,
#           "start_date": "2023-02-19"
#         },
#         {
#           "id": 32632446,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 23500,
#           "start_date": "2023-02-18"
#         },
#         {
#           "id": 32525975,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 23500,
#           "start_date": "2023-02-17"
#         },
#         {
#           "id": 32505141,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 22500,
#           "start_date": "2023-02-16"
#         },
#         {
#           "id": 32388045,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 23500,
#           "start_date": "2023-02-14"
#         },
#         {
#           "id": 32370201,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 23500,
#           "start_date": "2023-02-13"
#         },
#         {
#           "id": 32326013,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 23500,
#           "start_date": "2023-02-12"
#         },
#         {
#           "id": 32279869,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 23500,
#           "start_date": "2023-02-11"
#         },
#         {
#           "id": 32021379,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 24500,
#           "start_date": "2023-02-07"
#         },
#         {
#           "id": 31940016,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 24500,
#           "start_date": "2023-02-06"
#         },
#         {
#           "id": 31896620,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 24500,
#           "start_date": "2023-02-05"
#         },
#         {
#           "id": 31857231,
#           "all_lots_id": 48326564,
#           "auction_code": 2,
#           "price": 24500,
#           "start_date": "2023-02-04"
#         }
#       ]
#     },
#     {
#       "id": 79457178,
#       "auction_name": "COPART",
#       "body_style": None,
#       "car_keys": "yes",
#       "color": "BLACK",
#       "cylinders": "6",
#       "doc_type": "KY - CERT OF TITLE-SALVAGE",
#       "drive": "All wheel drive",
#       "engine_type": "3.8L  6",
#       "est_retail_value": 53855,
#       "fuel": "GAS",
#       "highlights": "RUNS AND DRIVES",
#       "location": "IL - CHICAGO SOUTH",
#       "lot_number": 63527563,
#       "make": "KIA",
#       "model": "TELLURIDE",
#       "odometer": 13561,
#       "primary_damage": "MINOR DENT/SCRATCHES",
#       "secondary_damage": None,
#       "seller": None,
#       "series": None,
#       "transmission": "AUTOMATIC",
#       "vehicle_type": "AUTOMOBILE",
#       "vin": "5XYP3DHC1NG225508",
#       "year": 2022,
#       "is_insurance": None,
#       "currency_code_id": 1,
#       "created_at": "2023-08-10 02:42:10",
#       "damage_photos": [],
#       "car_photo": {
#         "id": 19237684,
#         "all_lots_id": 79457178,
#         "photo": [
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/lpp/0823/702730d4113b443d8674e277e72be1e5_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/lpp/0823/df1ccda661034266891096032ef92cd5_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/lpp/0823/e6d4452fc0964d4e94f8a7bdd589d8a1_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/lpp/0823/86b032398fd643f08f8a9a35ee81cfc0_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/lpp/0823/6c606c0f3545435f8c2e03b5998773cb_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/lpp/0823/4378fc21580a4906a59be49961ca9f9d_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/lpp/0823/6ba6b0f5772b415bbe9a21b20f42a115_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/lpp/0823/80e225127b044f1cbb21c92c69644b16_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/lpp/0823/5fa5e5dea8944f54b2644e2a1e2b7303_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/lpp/0823/c0e34e55b72a47a1bc63fdf26d7cff68_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/lpp/0823/c1e105a6b8404e51b7cd453dd079a6a5_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/lpp/0823/486701c7625b46d1b749fe0578b3aa64_ful.jpg",
#           "https://cs.copart.com/v1/AUTH_svc.pdoc00001/lpp/0823/c83efb6d29404fb3b60f75ad76642c1e_ful.jpg"
#         ]
#       },
#       "car_info": {
#         "id": 21059817,
#         "all_lots_id": 79457178,
#         "make_id": 23,
#         "model_id": 724,
#         "series_id": 26011,
#         "vehicle_type_id": 2,
#         "body_class_id": 3,
#         "make": {
#           "id": 23,
#           "make": "KIA",
#           "make_slug": "kia",
#           "created_at": "2023-03-16 12:49:36",
#           "updated_at": "2023-03-16 10:50:37"
#         },
#         "model": {
#           "id": 724,
#           "model": "TELLURIDE",
#           "model_slug": "telluride",
#           "make_id": 23,
#           "created_at": "2023-03-16 12:50:14",
#           "updated_at": "2023-03-16 10:55:20"
#         },
#         "series": {
#           "id": 26011,
#           "series": "EX",
#           "model_id": 724
#         },
#         "vehicle_type": {
#           "id": 2,
#           "vehicle_type": "MULTIPURPOSE PASSENGER VEHICLE (MPV)"
#         },
#         "body_class": {
#           "id": 3,
#           "body_class": "SPORT UTILITY VEHICLE (SUV)/MULTI-PURPOSE VEHICLE (MPV)"
#         }
#       },
#       "sales_history": [
#         {
#           "id": 36482968,
#           "all_lots_id": 79457178,
#           "auction": 2,
#           "lot_number": 63527563,
#           "purchase_price": 22100,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 656089,
#           "buyer_state": "NY",
#           "buyer_country": "USA",
#           "sale_date": 1692194400,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 36668799,
#           "all_lots_id": 79457178,
#           "auction": 2,
#           "lot_number": 63527563,
#           "purchase_price": 23500,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 656089,
#           "buyer_state": "NY",
#           "buyer_country": "USA",
#           "sale_date": 1692666000,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 36671217,
#           "all_lots_id": 79457178,
#           "auction": 2,
#           "lot_number": 63527563,
#           "purchase_price": 25300,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": None,
#           "buyer_state": None,
#           "buyer_country": None,
#           "sale_date": 1692668767,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 56019069,
#           "all_lots_id": 79457178,
#           "auction": 2,
#           "lot_number": 63527563,
#           "purchase_price": 12600,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 656089,
#           "buyer_state": "NY",
#           "buyer_country": "USA",
#           "sale_date": 1736964000,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 56146986,
#           "all_lots_id": 79457178,
#           "auction": 2,
#           "lot_number": 63527563,
#           "purchase_price": 12700,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 656089,
#           "buyer_state": "NY",
#           "buyer_country": "USA",
#           "sale_date": 1737424800,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },        {
#           "id": 56399759,
#           "all_lots_id": 79457178,
#           "auction": 2,
#           "lot_number": 63527563,
#           "purchase_price": 12700,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 419403,
#           "buyer_state": "FL",
#           "buyer_country": "USA",
#           "sale_date": 1738029600,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 56399758,
#           "all_lots_id": 79457178,
#           "auction": 2,
#           "lot_number": 63527563,
#           "purchase_price": 12700,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 419403,
#           "buyer_state": "FL",
#           "buyer_country": "USA",
#           "sale_date": 1738029600,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#                 {
#           "id": 56756830,
#           "all_lots_id": 79457178,
#           "auction": 2,
#           "lot_number": 63527563,
#           "purchase_price": 9000,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 412519,
#           "buyer_state": "IL",
#           "buyer_country": "USA",
#           "sale_date": 1738778400,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 56903149,
#           "all_lots_id": 79457178,
#           "auction": 2,
#           "lot_number": 63527563,
#           "purchase_price": 15200,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 419403,
#           "buyer_state": "FL",
#           "buyer_country": "USA",
#           "sale_date": 1739239200,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 56903148,
#           "all_lots_id": 79457178,
#           "auction": 2,
#           "lot_number": 63527563,
#           "purchase_price": 15200,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 419403,
#           "buyer_state": "FL",
#           "buyer_country": "USA",
#           "sale_date": 1739239200,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 57005962,
#           "all_lots_id": 79457178,
#           "auction": 2,
#           "lot_number": 63527563,
#           "purchase_price": 5200,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 100081,
#           "buyer_state": "IL",
#           "buyer_country": "USA",
#           "sale_date": 1739383200,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 57112168,
#           "all_lots_id": 79457178,
#           "auction": 2,
#           "lot_number": 63527563,
#           "purchase_price": 9500,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 944653,
#           "buyer_state": "TX",
#           "buyer_country": "USA",
#           "sale_date": 1739556000,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },             {
#           "id": 61081609,
#           "all_lots_id": 79457178,
#           "auction": 2,
#           "lot_number": 63527563,
#           "purchase_price": 12800,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 419403,
#           "buyer_state": "FL",
#           "buyer_country": "USA",
#           "sale_date": 1748019600,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 61245967,
#           "all_lots_id": 79457178,
#           "auction": 2,
#           "lot_number": 63527563,
#           "purchase_price": 7300,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 419403,
#           "buyer_state": "FL",
#           "buyer_country": "USA",
#           "sale_date": 1748624400,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 61330511,
#           "all_lots_id": 79457178,
#           "auction": 2,
#           "lot_number": 63527563,
#           "purchase_price": 8300,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 200250,
#           "buyer_state": "OR",
#           "buyer_country": "USA",
#           "sale_date": 1748998800,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 61438032,
#           "all_lots_id": 79457178,
#           "auction": 2,
#           "lot_number": 63527563,
#           "purchase_price": 16600,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 419403,
#           "buyer_state": "FL",
#           "buyer_country": "USA",
#           "sale_date": 1749229200,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         },
#         {
#           "id": 61552932,
#           "all_lots_id": 79457178,
#           "auction": 2,
#           "lot_number": 63527563,
#           "purchase_price": 16600,
#           "sale_status": "Not sold",
#           "sold": 0,
#           "buyer_id": 680881,
#           "buyer_state": "XX",
#           "buyer_country": "   ",
#           "sale_date": 1749603600,
#           "auction_info": {
#             "auction_code": 2,
#             "country_name": "USA"
#           }
#         }
#       ],
#       "active_bidding": [],
#       "buy_now_car": {
#         "all_lots_id": 79457178,
#         "auction_name": "COPART",
#         "sale_date": "20250613",
#         "purchase_price": 18800
#       },
#       "currency": {
#         "id": 1,
#         "name": "US Dollar",
#         "char_code": "USD",
#         "iso_code": 840,
#         "code_id": 1
#       },
#       "buy_now_price_histories": [
#         {
#           "id": 62994760,
#           "all_lots_id": 79457178,
#           "auction_code": 2,
#           "price": 18800,
#           "start_date": "2025-06-13"
#         },  {
#           "id": 60090896,
#           "all_lots_id": 79457178,
#           "auction_code": 2,
#           "price": 20800,
#           "start_date": "2025-04-20"
#         },              {
#           "id": 58524070,
#           "all_lots_id": 79457178,
#           "auction_code": 2,
#           "price": 23200,
#           "start_date": "2025-03-11"
#         },        {
#           "id": 58214079,
#           "all_lots_id": 79457178,
#           "auction_code": 2,
#           "price": 23500,
#           "start_date": "2025-03-04"
#         },        {
#           "id": 57970786,
#           "all_lots_id": 79457178,
#           "auction_code": 2,
#           "price": 23500,
#           "start_date": "2025-02-27"
#         }  ]
#     }
#   ],
#   "api_request_left": 446640
# }

            if isinstance(response, dict):
                json_data = response 
            else:
                # If response is a real API call, parse it as JSON
                json_data = response.json()

            print("Response JSON:", json_data) 
            # Process the result
            if not json_data.get("result"):
                print(f"[EMPTY] No result for VIN {vin}")
                vehicle.to_be_updated = False
                vehicle.save(update_fields=["to_be_updated"])
                return JsonResponse({"message": "No result found for VIN."})

            with transaction.atomic():
                for data in json_data["result"]:
                    vin = data.get("vin")

                    if vin:
                        # Extract and save car_info data
                        car_info_data = data.get("car_info", {})
                        car_info_obj = update_or_create_car_info(car_info_data)
                        if car_info_obj:
                            vehicle.car_info = car_info_obj

                        # Extract and save additional vehicle data
                        vehicle.auction_name = data.get("auction_name")
                        vehicle.body_style = data.get("body_style")
                        vehicle.car_keys = data.get("car_keys")
                        vehicle.color = data.get("color")
                        vehicle.cylinders = data.get("cylinders")
                        vehicle.drive = data.get("drive")
                        vehicle.engine_type = data.get("engine_type")
                        vehicle.est_retail_value = data.get("est_retail_value")
                        vehicle.fuel = data.get("fuel")
                        vehicle.location = data.get("location")
                        vehicle.lot_number = data.get("lot_number")
                        vehicle.make = data.get("make")
                        vehicle.model = data.get("model")
                        vehicle.odometer = data.get("odometer")
                        vehicle.primary_damage = data.get("primary_damage")
                        vehicle.seller = data.get("seller")
                        vehicle.series = data.get("series")
                        vehicle.transmission = data.get("transmission")
                        vehicle.vehicle_type = data.get("vehicle_type")
                        vehicle.year = data.get("year")

                        # Handle car photo URLs
                        car_photo_data = data.get("car_photo", {}).get("photo", [])
                        if car_photo_data:
                            vehicle.car_photo_urls = car_photo_data

                        # Handle damage photos
                        damage_photos = data.get("damage_photos", [])
                        if damage_photos:
                            vehicle.damage_photos = damage_photos

                        
                        # Ensure that the sales_history field is initialized as a list if it doesn't exist
                        if not isinstance(vehicle.sales_history, list):
                            vehicle.sales_history = []

                        # Get all sales_history data from the API response
                        sales_history_data = data.get("sales_history", [])

                        # Iterate through all sales_history items in the response
                        for sale in sales_history_data:
                            sale_data = {}

                            # Loop through each key-value pair in the sale data dynamically and add it to sale_data
                            for key, value in sale.items():
                                # Handle null values (e.g., "null" string to None)
                                sale_data[key] = handle_null_values(value)  # Dynamically handling null strings

                            # Append the dynamically collected sale_data to the vehicle's sales_history
                            vehicle.sales_history.append(sale_data)

                        # Save the vehicle with the updated sales_history
                        vehicle.save(update_fields=["sales_history"])


                        # Save vehicle data
                        save_vehicle_data(vehicle, data)
                    print(f"[✓] Updated vehicle: {vin}")

            # After successfully processing, mark the vehicle as updated
            vehicle.to_be_updated = False
            vehicle.save(update_fields=["to_be_updated"])
            
            time.sleep(1)

            return render(request, 'manual-vin-form.html')

        except Exception as e:
            print(f"[VIN ERROR] Exception for VIN {vin}: {e}")
            vehicle.to_be_updated = False
            vehicle.save(update_fields=["to_be_updated"])
            return render(request, 'manual-vin-form.html',{"error": f"Error processing VIN {vin}: {str(e)}"}, status=500)

    return render(request, 'manual-vin-form.html', {
        'api_token': default_token
    })

def contact_us(request):
    return render(request, 'contact-us.html')

# Utility to safely convert string to float
def safe_float(value):
    if value is None:
        return None
    value = value.strip().lower()
    if value in ['null', '', 'none']:
        return None
    try:
        return float(value)
    except ValueError:
        return None


# Utility to safely convert string to int
def safe_int(value):
    if value is None:
        return None
    value = value.strip().lower()
    if value in ['null', '', 'none']:
        return None
    try:
        return int(value)
    except ValueError:
        return None


@csrf_exempt
def upload_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file or not csv_file.name.endswith('.csv'):
            return JsonResponse({'message': 'Please upload a valid CSV file.'}, status=400)

        try:
            data = csv_file.read().decode('utf-8')
            io_string = io.StringIO(data)
            reader = csv.DictReader(io_string)

            existing_lot_ids = set(Vehicle.objects.values_list('lot_id', flat=True))
            vehicles_to_create = []
            skipped_count = 0
            added_count = 0

            for row in reader:
                lot_id = row.get("lot_id")
                if not lot_id:
                    skipped_count += 1
                    continue

                lot_id_int = safe_int(lot_id)
                if lot_id_int in existing_lot_ids:
                    skipped_count += 1
                    continue

                vehicle = Vehicle(
                    lot_id=lot_id_int,
                    vin=row.get("vin"),
                    auction_name=row.get("auction_name"),
                    make=row.get("make"),
                    model=row.get("model"),
                    year=safe_int(row.get("year")),
                    body_style=row.get("body_style"),
                    car_keys=row.get("car_keys"),
                    color=row.get("color"),
                    cylinders=row.get("cylinders"),
                    doc_type=row.get("doc_type"),
                    drive=row.get("drive"),
                    engine_type=row.get("engine_type"),
                    est_retail_value=safe_float(row.get("est_retail_value")),
                    fuel=row.get("fuel"),
                    highlights=row.get("highlights"),
                    location=row.get("location"),
                    lot_number=safe_int(row.get("lot_number")),
                    odometer=safe_float(row.get("odometer")),
                    primary_damage=row.get("primary_damage"),
                    secondary_damage=row.get("secondary_damage"),
                    seller=row.get("seller"),
                    series=row.get("series"),
                    transmission=row.get("transmission"),
                    vehicle_type=row.get("vehicle_type"),
                    is_insurance=row.get("is_insurance").lower() == 'true' if row.get("is_insurance") else None,
                    currency_name=row.get("currency_name"),
                    currency_code=row.get("currency_code"),
                    created_at=now(),
                    updated_at=now()
                )
                vehicles_to_create.append(vehicle)
                added_count += 1

            Vehicle.objects.bulk_create(vehicles_to_create)

            return JsonResponse({
                'message': f'Success: {added_count} vehicles added. {skipped_count} skipped (duplicates or invalid).'
            })

        except Exception as e:
            return JsonResponse({'message': f'Error while processing file: {str(e)}'}, status=500)

    return JsonResponse({'message': 'Invalid request method.'}, status=405)


@csrf_exempt 
def trigger_vechile_vin(request):
    if request.method == "POST":
        try:
            vehicles = get_all_to_be_updated()            
            # vehicles = get_latest_5_to_be_updated()
            fetch_car_vin_data(vehicles)
            # fetch_car_vin_data(vehicles)
            return JsonResponse({"status": "success", "message": "VIN data updated successfully."}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Only POST method is allowed."}, status=405)




def sitemap_view(request):
    vehicles = Vehicle.objects.all()
    paginator = Paginator(vehicles, 100)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    
    # Debugging: Print page numbers and the count of vehicles
    print(f"Page Number: {page_number}")
    print(f"Total Vehicles: {vehicles.count()}")
    print(f"Has Next: {page.has_next()}")
    print(f"Has Previous: {page.has_previous()}")
    
    return render(request, 'sitemap.xml', {'cars': page})
