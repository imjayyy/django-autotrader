
from datetime import datetime
from django.http import JsonResponse
from vehicles.models import SuperuserLastSearch,Vehicle,Vehicle

MAX_LENGTH = 100


def value_in_list(value, valid_list):
    return str(value).lower() in [str(v).lower() for v in valid_list]

def safe_date(date_str):
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
    except:
        return None

# def get_field_counts(queryset, field_name):
#     return queryset.values(field_name).distinct().annotate(count=Count(field_name)).order_by(field_name.lower())

def get_field_counts(queryset, field):
    """
    Returns a list of dicts with unique, Title Cased values and their counts, case-insensitive.
    E.g. [{ 'make': 'Ford', 'count': 3 }, ...]
    """
    from collections import defaultdict
    field_counter = defaultdict(int)
    field_name = field if '__' not in field else field.split('__')[-1]
    values = queryset.values_list(field, flat=True)
    for val in values:
        if val:
            clean = str(val).strip().lower()
            field_counter[clean] += 1
    return [
        {field_name: key.title(), 'count': count}
        for key, count in sorted(field_counter.items())
    ]

def get_currency_names(queryset):
    return get_field_counts(queryset, 'currency_name')

def get_buy_now_options(vehicles_qs):
    # Generate options for the 'Buy Now' field from the vehicles queryset
    options = [
        {'value': 'yes', 'count': vehicles_qs.filter(buy_now_car__isnull=False).count()},
        {'value': 'no', 'count': vehicles_qs.filter(buy_now_car__isnull=True).count()},
    ]
    return options

def save_vehicle_filters(request):
    if request.method == "POST":
        # Get form data as dict
        filters = request.POST.dict()
        filters.pop('csrfmiddlewaretoken', None)  # Clean up

        # Save to single row (use update_or_create if needed)
        obj, _ = SuperuserLastSearch.objects.get_or_create(pk=1)
        obj.filters = filters
        obj.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)

def truncate_string(value):
    if value and len(value) > MAX_LENGTH:
        return value[:MAX_LENGTH]
    return value

def get_latest_5_to_be_updated():
    # Fetch the latest 5 vehicles that need to be updated as model instances
    vehicles = Vehicle.objects.filter(to_be_updated=True).order_by('-created_at')[:5]
    return vehicles  # Now returns actual Vehicle instances, not dictionaries

def get_latest_10_to_be_updated():
    # Fetch the latest 5 vehicles that need to be updated as model instances
    vehicles = Vehicle.objects.filter(to_be_updated=True).order_by('-created_at')[:10]
    return vehicles  # Now returns actual Vehicle instances, not dictionaries


def get_all_to_be_updated():
    # Fetch the latest 5 vehicles that need to be updated as model instances
    vehicles = Vehicle.objects.filter(to_be_updated=True).order_by('-created_at')
    return vehicles 


def handle_null_values(data):
    # Check if data is a string and equals to "null" or curly quotes versions
    if isinstance(data, str):
        data = data.strip()  # Remove any surrounding whitespace
        if data.lower() in ["null", "“null”", "”null“"]:
            return None
    return data