import requests
from datetime import datetime
from django.shortcuts import render
from .models import Vehicle, CarInfo
import time,os
from django.db import transaction
from django.shortcuts import render
from django.utils import timezone
from vehicles.utils import truncate_string,handle_null_values

api_token = '6394dc91ece3542af402645dc9f2aa1b2c2dec923b24cf3d249373228a019684'


LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), "livelogfile.log")

def log_message(msg):
    # Ensure the directory exists
    log_dir = os.path.dirname(LOG_FILE_PATH)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    print(msg)  # still shows in terminal
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(f"{msg}\n")

# Helper to convert string dates
def parse_dt(value):
    try:
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return timezone.make_aware(dt, timezone.get_default_timezone())
    except Exception:
        return None


def safe_float(val):
    try:
        return float(val)
    except:
        return None
import json

def fetch_data_with_retry(url, body, headers, retries=3, delay=5):
    for attempt in range(retries):
        debug_line = f"[DEBUG] Sending body: {body} to URL: {url}"
        print(debug_line)
        try:
            response = requests.post(url, json=body, headers=headers, timeout=30)
            if response.status_code == 200:
                return response
            elif response.status_code == 422:
                line = "API returned 422 Unprocessable Entity. Check your params and their format."
                print(line)
                print("Body sent:", body)
                break
            else:
                line = f"Attempt {attempt + 1}: Status {response.status_code}"
                print(line)
        except Exception as e:
            line = f"Attempt {attempt + 1}: Exception {e}"
            print(line)
        time.sleep(delay)
    return None

def fetch_data_with_retry_manuall(api_url, body, headers, max_retries=3, delay=2):
    import requests, traceback
    for attempt in range(max_retries):
        try:
            print(f"[INFO] Attempt {attempt+1} — Fetching: {api_url}")
            print(f"[DEBUG] Payload: {json.dumps(body)}")
            response = requests.post(api_url, json=body, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[RETRY {attempt + 1}] Error: {e}")
            traceback.print_exc()
            time.sleep(delay)
            delay *= 2  # exponential backoff
    return None

def update_or_create_car_info(car_info_data):
    if not isinstance(car_info_data, dict):
        return None

    all_lots_id = car_info_data.get("all_lots_id")
    if not all_lots_id:
        return None

    defaults = {
        "make": car_info_data.get("make", {}).get("make"),
        "model": car_info_data.get("model", {}).get("model"),
        "series": car_info_data.get("series", {}).get("series"),
        "vehicle_type": car_info_data.get("vehicle_type", {}).get("vehicle_type"),
        "body_class": car_info_data.get("body_class", {}).get("body_class"),
        "make_id": car_info_data.get("make_id"),
        "model_id": car_info_data.get("model_id"),
        "series_id": car_info_data.get("series_id"),
        "vehicle_type_id": car_info_data.get("vehicle_type_id"),
        "body_class_id": car_info_data.get("body_class_id"),
    }
    car_info_obj, created = CarInfo.objects.update_or_create(
        all_lots_id=all_lots_id,
        defaults=defaults
    )
    return car_info_obj


def save_vehicle_data(vehicle_obj, data):
    # Map API fields to your Vehicle model fields
    vehicle_obj.lot_id = data.get("lot_id") 
    vehicle_obj.vin = data.get("vin") or vehicle_obj.vin
    vehicle_obj.auction_name = data.get("auction_name")
    vehicle_obj.make = data.get("make")
    vehicle_obj.model = data.get("model")
    vehicle_obj.year = data.get("year")
    vehicle_obj.body_style = data.get("body_style")
    vehicle_obj.car_keys = data.get("car_keys")
    vehicle_obj.color = data.get("color")
    vehicle_obj.cylinders = data.get("cylinders")
    vehicle_obj.doc_type = data.get("doc_type")
    vehicle_obj.drive = data.get("drive")
    vehicle_obj.engine_type = data.get("engine_type")
    vehicle_obj.est_retail_value = data.get("est_retail_value")
    vehicle_obj.fuel = data.get("fuel")
    vehicle_obj.highlights = data.get("highlights")
    vehicle_obj.location = data.get("location") or vehicle_obj.location
    vehicle_obj.lot_number = data.get("lot_number")
    vehicle_obj.odometer = data.get("odometer")
    vehicle_obj.primary_damage = data.get("primary_damage")
    vehicle_obj.secondary_damage = data.get("secondary_damage")
    vehicle_obj.seller = data.get("seller")
    vehicle_obj.series = data.get("series")
    vehicle_obj.transmission = data.get("transmission")
    vehicle_obj.vehicle_type = data.get("vehicle_type")
    vehicle_obj.is_insurance = data.get("is_insurance")
    vehicle_obj.currency_name = data.get("currency", {}).get("name")
    vehicle_obj.currency_code = data.get("currency", {}).get("char_code")

    # Save photos arrays
    car_photo_obj = data.get("car_photo")
    if car_photo_obj:
        vehicle_obj.car_photo_urls = car_photo_obj.get("photo", [])
    else:
        vehicle_obj.car_photo_urls = []

    damage_photos = data.get("damage_photos")
    if damage_photos and isinstance(damage_photos, list):
        vehicle_obj.damage_photos = damage_photos
    else:
        vehicle_obj.damage_photos = []

    # JSON fields
    vehicle_obj.buy_now_price_histories = data.get("buy_now_price_histories") or []

    previous_vehicle_obj_sales_history = vehicle_obj.sales_history or []
    new_vehicle_obj_sales_history = data.get("sales_history") or []
    latest_vehicle_sales_history = previous_vehicle_obj_sales_history
    for vehicle in new_vehicle_obj_sales_history:
        latest_vehicle_sales_history.append(vehicle)

    vehicle_obj.sales_history = latest_vehicle_sales_history
    
    vehicle_obj.active_bidding = data.get("active_bidding") or []
    vehicle_obj.buy_now_car = data.get("buy_now_car") or {}
    vehicle_obj.save()


def fetch_vehicle_data(filters):
    url = "https://copart-iaai-api.com/api/v2/get-cars"
    api_token = filters.get("api_token")
    page = filters.get("page", 1)
    per_page = 50
    url = f"{url}?api_token={api_token}&page={page}&per_page={per_page}"

    body = {k: v for k, v in filters.items() if k not in ['api_token', 'page', 'per_page'] and v not in [None, '', 'null']}
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    response = fetch_data_with_retry(url, body, headers)
    if not response:
        line = "[API ERROR] Failed to fetch data after retries"
        print(line)
        return {"error": "Failed to fetch data after retries"}, {"saved": 0, "duplicates": 0, "invalid": 0}

    line1 = f"API Response status: {response.status_code}"
    print(line1)
    log_message(line1)
    line = f"API Response content: {response.text}"
    log_message(line)
    print(line)

    saved, duplicates, invalid = 0, 0, 0
    data = response.json()

    for item in data.get("result", []):
        if not item.get("vin"):
            invalid += 1
            continue
        try:
            incoming_updated_at = parse_dt(item.get("updated_at"))
            currency = item.get("currency") or {}
             # Check if the VIN already exists in the database
            vehicle_obj = Vehicle.objects.filter(vin=item["vin"]).first()
            if not vehicle_obj:
                with transaction.atomic():
                    vehicle_obj, created = Vehicle.objects.get_or_create(
                    vin=item["vin"],
                    defaults={
                        "lot_id": item["id"],
                        "auction_name": truncate_string(item.get("auction_name")),
                        "make": truncate_string(item.get("make")),
                        "model": truncate_string(item.get("model")),
                        "year": item.get("year"),
                        "body_style": item.get("body_style"),
                        "car_keys": item.get("car_keys", "no"),
                        "color": item.get("color"),
                        "cylinders": item.get("cylinders"),
                        "doc_type": item.get("doc_type"),
                        "drive": item.get("drive"),
                        "engine_type": item.get("engine_type"),
                        "est_retail_value": safe_float(item.get("est_retail_value")),
                        "fuel": item.get("fuel"),
                        "highlights": item.get("highlights"),
                        "location": item.get("location"),
                        "lot_number": item.get("lot_number"),
                        "odometer": safe_float(item.get("odometer")),
                        "primary_damage": item.get("primary_damage"),
                        "secondary_damage": item.get("secondary_damage"),
                        "seller": item.get("seller"),
                        "series": item.get("series"),
                        "transmission": item.get("transmission"),
                        "vehicle_type": item.get("vehicle_type"),
                        "is_insurance": item.get("is_insurance", False),
                        "currency_name": currency.get("name"),
                        "currency_code": currency.get("char_code"),
                        "car_photo_urls": item.get("car_photo", {}).get("photo", []),
                        "damage_photos": item.get("damage_photos") or [],
                        "buy_now_price_histories": item.get("buy_now_price_histories") or {},
                        "sales_history": item.get("sales_history") or {},
                        "active_bidding": item.get("active_bidding") or {},
                        "buy_now_car": item.get("buy_now_car") or {},
                        "to_be_updated": True
                    }
                )

                if created:
                    # If the record was newly created, don't set `updated_at` at this stage
                    print(f"[CREATED] New record created for VIN: {item['vin']}")
                else:
                    # If the record already exists, update the `updated_at` field
                    incoming_updated_at = parse_dt(item.get("updated_at"))
                    if vehicle_obj.updated_at != incoming_updated_at:
                        vehicle_obj.updated_at = incoming_updated_at
                        vehicle_obj.to_be_updated = True
                        vehicle_obj.save(update_fields=["updated_at", "to_be_updated"])
                        print(f"[UPDATED] Existing record updated for VIN: {item['vin']}")
                    else:
                        print(f"[DUPLICATE] No update required for VIN: {item['vin']}")

        except Exception as e:
            err_line = f"[SAVE ERROR] Failed to save vehicle {item.get('vin', 'unknown vin')}: {e}"
            print(err_line)
            continue

    summary_line = f"[PAGE SUMMARY] Saved: {saved}, Duplicates: {duplicates}, Invalid: {invalid}"
    print(summary_line)
    log_message(summary_line)

    time.sleep(1)
    next_line = "[NEXT] Starting VIN-level update for saved vehicles..."
    log_message(next_line)
    print(next_line)
    return data, {"saved": saved, "duplicates": duplicates, "invalid": invalid}


# Wrapper to fetch multiple pages with delay
def fetch_multiple_pages(filters, max_pages=10):
    all_data = []
    total_summary = {"saved": 0, "duplicates": 0, "invalid": 0}

    start_page = int(filters.get("page", 1))

    for page in range(start_page, start_page + max_pages):
        filters["page"] = page
        log_message(f"Fetching page {page}...")
        print(f"Fetching page {page}...")

        data, summary = fetch_vehicle_data(filters)

        if "error" in data:
            print(f"Error fetching page {page}: {data['error']}")
            break

        all_data.append(data)
        total_summary["saved"] += summary["saved"]
        total_summary["duplicates"] += summary["duplicates"]
        total_summary["invalid"] += summary["invalid"]

        total_pages = data.get("pagination", {}).get("total_pages")
        if total_pages and page >= total_pages:
            print(f"Reached last page: {page}")
            break
        time.sleep(1)

    print("All pages fetched.")
    return all_data, total_summary



HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Authorization": f"Bearer {api_token}"  # Adding the token in the Authorization header
}

def fetch_car_vin_data(vehicles):
    if not vehicles:
        print("[INFO] No vehicles to process. All vehicles already up-to-date.")
        return

    processed_vins = set()  # Set to track processed VINs
    for vehicle in vehicles:
        # Skip if already processed (even if somehow flagged as True)
        if vehicle.vin in processed_vins:
            print(f"[SKIPPED] VIN {vehicle.vin} already processed.")
            continue
        
        # Add to processed set to avoid future duplicates in the current run
        processed_vins.add(vehicle.vin)

        print(f"[✓] VIN update job started for {vehicle.vin}...")

        # Build query params
        params = {
            "api_token": api_token,
            "vin_number": vehicle.vin,
            "only_with_color": 0
        }
        try:
        

            response = requests.post(
                "https://copart-iaai-api.com/api/v1/get-car-vin",
                params=params,
                headers=HEADERS,
                data=''
            )
            # For now, use the hardcoded response (for testing purposes)
            # response = {
            #     'result': [
            #         {
            #             'id': 386911138,
            #             'auction_name': 'COPART',
            #             'body_style': None,
            #             'car_keys': 'yes',
            #             'color': 'CHARCOAL',
            #             'cylinders': '8',
            #             'drive': '4x4 w/Rear Wheel Drv',
            #             'engine_type': '5.7L  8',
            #             'est_retail_value': 26079,
            #             'fuel': 'GAS',
            #             'location': 'FL - ORLANDO SOUTH',
            #             'lot_number': 65056014,
            #             'make': 'RAM',
            #             'model': '1500',
            #             'odometer': 99107,
            #             'primary_damage': 'FRONT END',
            #             'seller': 'GEICO',
            #             'series': 'BIG H',
            #             'transmission': 'AUTOMATIC',
            #             'vin': '1C6SRFFT8LN378827',
            #             'year': 2020,
            #             'car_photo': {
            #                 'photo': [
            #                     'https://cs.copart.com/v1/AUTH_svc.pdoc00001/ids-c-prod-lpp/0724/097d296042034016a1da433fd6e953af_hrs.jpg',
            #                     'https://cs.copart.com/v1/AUTH_svc.pdoc00001/ids-c-prod-lpp/0724/d860c9e0dc2241f8b9685a2ae495adfa_hrs.jpg',
            #                     # more photos...
            #                 ]
            #             },
            #             'sales_history': [
            #                 {
            #                     'purchase_price': 12000,
            #                     'sale_status': 'Sold',
            #                     'buyer_state': 'FL',
            #                     'sale_date': '1747317600',
            #                 },{
            #                     'purchase_price': 12000,
            #                     'sale_status': 'Sold',
            #                     'buyer_state': 'FL',
            #                     'sale_date': '1747317600',
            #                 }
            #             ],
            # 'sales_history': [
            #                 {
            #                     'purchase_price': 12000,
            #                     'sale_status': 'Sold',
            #                     'buyer_state': 'FL',
            #                     'sale_date': '1747317600',
            #                 },{
            #                     'purchase_price': 12000,
            #                     'sale_status': 'Sold',
            #                     'buyer_state': 'FL',
            #                     'sale_date': '1747317600',
            #                 }
            #             ],
            #  "buy_now_price_histories": [
            #         {
            #         "id": 62922114,
            #         "all_lots_id": 79457178,
            #         "auction_code": 2,
            #         "price": 18800,
            #         "start_date": "2025-06-12"
            #         },
            #         {
            #         "id": 62787120,
            #         "all_lots_id": 79457178,
            #         "auction_code": 2,
            #         "price": 18800,
            #         "start_date": "2025-06-10"
            #         }
                    #   ]
                    # }

            # Check if response is a dict (in case of hardcoded response)
            if isinstance(response, dict):
                json_data = response 
            else:
                # If response is a real API call, parse it as JSON
                json_data = response.json()

            print("Response JSON:", json_data) 
            # Process the result
            # if not json_data.get("result"):
            #     print(f"[EMPTY] No result for VIN {vin}")
            #     vehicle.to_be_updated = False
            #     vehicle.save(update_fields=["to_be_updated"])
            #     return render('manual-vin-form.html',{"message": "No result found for VIN."})

            # with transaction.atomic():
            #     for data in json_data["result"]:
            #         vin = data.get("vin")
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
                        # Handle car photo URLs
                        car_photo_data = data.get("car_photo", {}).get("photo", [])
                        if car_photo_data:
                            vehicle.car_photo_urls = car_photo_data

                        # Handle damage photos
                        damage_photos = data.get("damage_photos", [])
                        if damage_photos:
                            vehicle.damage_photos = damage_photos
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

        except Exception as e:
            print(f"[VIN ERROR] Exception for VIN {vehicle.vin}: {e}")
            # vehicle.to_be_updated = False
            # vehicle.save(update_fields=["to_be_updated"])
            continue



def trigger_car_vin_data(vehicles):
    if not vehicles:
        print("[INFO] No vehicles to process. All vehicles already up-to-date.")
        return

    processed_vins = set()  # Set to track processed VINs

    for vehicle in vehicles:
        # Skip if already processed (even if somehow flagged as True)
        if vehicle.vin in processed_vins:
            print(f"[SKIPPED] VIN {vehicle.vin} already processed.")
            continue

        # Add to processed set to avoid future duplicates in the current run
        processed_vins.add(vehicle.vin)

        print(f"[✓] VIN update job started for {vehicle.vin}...")

        # Build query params
        params = {
            "api_token": api_token,
            "vin_number": vehicle.vin,
            "only_with_color": 0
        }

        try:
            response = requests.post(
                "https://copart-iaai-api.com/api/v1/get-car-vin",
                params=params,
                headers=HEADERS,
                data=''
            )

            if isinstance(response, dict):
                json_data = response  # If it's already a dictionary, skip .json() parsing
            else:
                # If response is a real API call, parse it as JSON
                json_data = response.json()

            print("Response JSON:", json_data)  # Printing the full JSON response

            # Process the result
            if not json_data.get("result"):
                print(f"[EMPTY] No result for VIN {vehicle.vin}")
                vehicle.to_be_updated = False
                vehicle.save(update_fields=["to_be_updated"])
                continue

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

                        # Handle sales history
                        sales_history = data.get("sales_history", [])
                        if sales_history:
                            vehicle.sales_history = sales_history

                        # Save vehicle data
                        save_vehicle_data(vehicle, data)
                        print(f"[✓] Updated vehicle: {vin}")
                        time.sleep(1)

            # After successfully processing, mark the vehicle as updated
            vehicle.to_be_updated = False
            vehicle.save(update_fields=["to_be_updated"])

        except Exception as e:
            print(f"[VIN ERROR] Exception for VIN {vehicle.vin}: {e}")
            vehicle.to_be_updated = False
            vehicle.save(update_fields=["to_be_updated"])
            continue

