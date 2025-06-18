from .models import AuctionDetail, AuctionActiveBid, AuctionCurrency, Auction, BuyNowPriceHistory
from .models import AuctionVehicle as Vehicle
from .models import AuctionVehicleMedia as VehicleMedia
from car_details.models import Make, Model, Fuel, BodyStyle, Transmission, Drive, Color, Country, Status
from django.utils.timezone import make_aware
import datetime
from django.utils.dateparse import parse_datetime


def map_api_data_to_auction_data(auction):
    """
    Maps API data to auction data format.

    Args:
        auction (dict): The API data to map.

    Returns:
        dict: The mapped auction data.
    """
    
    Vehicle.objects.filter(VIN=auction['vin']).delete()  # Clear existing records for the same VIN

    sales_history = auction.get('sales_history', [])
    sales_history = sales_history[-1] if sales_history!=[] else {}

    # last_sale = sales_history[-1] if sales_history else {}
    buy_now_price_histories = auction.get('buy_now_price_histories', {})
    currency_code = auction.get('currency', {}).get('char_code')
    active_bidding = auction.get('active_bidding', [])
    active_bidding = active_bidding[-1] if active_bidding!=[] else {}

    make_obj, _ = Make.objects.get_or_create(name=auction['make'])
    model_obj, _ = Model.objects.get_or_create(name=auction['model'], make=make_obj)
    fuel_obj, _ = Fuel.objects.get_or_create(name_en=auction['fuel'], defaults={'name_en': auction['fuel']})                
    body_style_obj, _ = BodyStyle.objects.get_or_create(name_en=auction['body_style'], defaults={'name_en': auction['body_style']})
    transmission_obj, _ = Transmission.objects.get_or_create(name_en=auction['transmission'], defaults={'name_en': auction['transmission']})
    drive_obj, _ = Drive.objects.get_or_create(name_en=auction['drive'], defaults={'name_en': auction['drive']})
    color_obj, _ = Color.objects.get_or_create(name_en=auction['color'], defaults={'name_en': auction['color']})

    country_obj = Country.objects.first()
    status_obj = Status.objects.first()
    created_at_raw = auction.get('created_at')

    if isinstance(created_at_raw, str):
        created_at = make_aware(datetime.datetime.strptime(created_at_raw, "%Y-%m-%d %H:%M:%S"))
    else:
        created_at = datetime.datetime.now()   # or `None` if allowed

    auctionvehicle = Vehicle.objects.create(
        make=make_obj,
        model=model_obj,
        fuel=fuel_obj,
        body_style=body_style_obj,
        transmission=transmission_obj,
        drive=drive_obj,
        color=color_obj,
        country=country_obj,
        cylinders=int(auction.get('cylinders', 0)) if auction.get('cylinders') else None,
        status=status_obj,
        odometer=auction.get('odometer'),
        year=auction.get('year'),
        engine_type=auction.get('engine_type'),
        VIN=auction.get('vin'),
        currency=currency_code,
        price=auction.get('est_retail_value', 0),
        number_of_seats=5,
        is_published=True,
        is_popular=False,
        to_be_updated=True
    )

    auction_company, _ = Auction.objects.get_or_create(auction_name=auction.get('auction_name'))

    auction_obj = AuctionDetail.objects.create(
        auctionvehicle=auctionvehicle,
        auction=auction_company,
        lot_number=auction.get('lot_number'),
        car_keys=auction.get('car_keys'),
        primary_damage=auction.get('primary_damage'),
        secondary_damage=auction.get('secondary_damage'),
        highlights=auction.get('highlights'),
        location=auction.get('location'),
        est_retail_value=auction.get('est_retail_value'),
        vin=auction.get('vin'),

        sale_date = make_aware(datetime.datetime.fromtimestamp(int(active_bidding['sale_date']) / 1000)) if active_bidding.get('sale_date') else None,

        sale_status=sales_history.get('sale_status'),
        purchase_price=sales_history.get('purchase_price'),
        buyer_country=sales_history.get('buyer_country'),
        created_at=datetime.datetime.now(),
    )

    # Optional: store historical prices
    for history in buy_now_price_histories:
        BuyNowPriceHistory.objects.create(
            vehicle=auctionvehicle,
            start_date=history.get('start_date'),
            price=history.get('price')
        )

    # Save media
    for photo_url in auction.get('car_photo', {}).get('photo', []):
        VehicleMedia.objects.create(
            vehicle=auctionvehicle,
            all_lots_id=auction['id'],
            vin=auction['vin'],
            img_url_from_api=photo_url,
            image_path=photo_url
        )




def map_response_to_models_single_vehicle(response_data):
    result = response_data["result"][0]

    # Get or create related fields
    make, _ = Make.objects.get_or_create(name=result["make"])
    model, _ = Model.objects.get_or_create(name=result["model"], make=make)
    fuel, _ = Fuel.objects.get_or_create(name_en=result.get("fuel") or "Unknown")
    body_style, _ = BodyStyle.objects.get_or_create(name_en=result.get("body_style") or "Unknown")
    transmission, _ = Transmission.objects.get_or_create(name_en=result.get("transmission") or "Unknown")
    drive, _ = Drive.objects.get_or_create(name_en=result.get("drive") or "Unknown")
    color, _ = Color.objects.get_or_create(name_en=result.get("color") or "Unknown")
    country_name = result["active_bidding"][0]["auction_info"].get("country_name", "Unknown")
    country, _ = Country.objects.get_or_create(name=country_name)

    # Create AuctionVehicle
    auction_vehicle = Vehicle.objects.create(
        make=make,
        model=model,
        fuel=fuel,
        body_style=body_style,
        transmission=transmission,
        drive=drive,
        color=color,
        country=country,
        cylinders=result.get("cylinders") or None,
        odometer=result.get("odometer"),
        year=result.get("year"),
        engine_type=result.get("engine_type"),
        VIN=result.get("vin"),
        currency=result["currency"]["char_code"],
        price=result.get("est_retail_value"),
    )

    # Get or create Auction
    auction, _ = Auction.objects.get_or_create(auction_name=result["auction_name"])

    # Get or create Currency
    currency_data = result["currency"]
    currency, _ = AuctionCurrency.objects.get_or_create(
        code_id=currency_data["code_id"],
        defaults={
            "name": currency_data["name"],
            "char_code": currency_data["char_code"],
            "iso_code": currency_data["iso_code"],
        }
    )

    # Create AuctionDetail
    auction_detail = AuctionDetail.objects.create(
        auctionvehicle=auction_vehicle,
        auction=auction,
        lot_number=result["lot_number"],
        car_keys=result.get("car_keys"),
        primary_damage=result.get("primary_damage"),
        secondary_damage=result.get("secondary_damage"),
        highlights=result.get("highlights"),
        location=result.get("location"),
        est_retail_value=result.get("est_retail_value"),
        vin=result["vin"],
        created_at=parse_datetime(result["created_at"]),
        currency=currency,
    )

    # Create Active Bidding
    for bidding in result["active_bidding"]:
        active_bid = AuctionActiveBid.objects.create(
            auction=bidding["auction"],
            all_lots_id=bidding["all_lots_id"],
            sale_date=int(bidding["sale_date"]),
            current_bid=bidding["current_bid"],
            date_updated=bidding["date_updated"],
            bid_updated=bidding["bid_updated"],
        )
        auction_detail.active_bidding.add(active_bid)

    # Save car photos
    car_photos = result.get("car_photo", {}).get("photo", [])
    for url in car_photos:
        VehicleMedia.objects.create(
            img_url_from_api=url,
            vin=result["vin"],
            all_lots_id=result["id"],
            vehicle=auction_vehicle,
        )

    return auction_vehicle, auction_detail




