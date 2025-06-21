from django.contrib import admin
from .models import CarInfo, Vehicle
from django.http import HttpResponseRedirect
from django.urls import path
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import Widget, DateTimeWidget
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .models import Vehicle
from datetime import datetime, timezone
from django.utils.timezone import make_aware, utc

@admin.register(CarInfo)
class CarInfoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'all_lots_id', 'make', 'model', 'series',
        'vehicle_type', 'body_class',
        'make_id', 'model_id', 'series_id', 'vehicle_type_id', 'body_class_id'
    )
    search_fields = ('make', 'model', 'series')
    list_filter = ('make', 'vehicle_type', 'body_class')




class CarInfoCreateEveryTimeWidget(Widget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None

        # Create a new CarInfo every time, based on CSV row values
        return CarInfo.objects.create(
            all_lots_id=row.get("Lot number"),  # You must ensure uniqueness
            make=row.get("Make"),
            model=row.get("Model Group"),
            series=row.get("Trim"),
            vehicle_type=row.get("Vehicle Type"),
            body_class=row.get("Body Style"),
        )

    def render(self, value, obj=None):
        return value.model if value else ""
    
class FlexibleDateTimeWidget(DateTimeWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None
        
        value = value.strip()

        # Handle ISO 8601 with Z (UTC)
        if value.endswith("Z"):
            try:
                dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
                return dt.replace(tzinfo=utc)
            except ValueError:
                pass

        formats_to_try = [
            "%Y-%m-%d-%H.%M.%S.%f",     # Your format: 2025-06-19-08.10.17.000617
            "%Y-%m-%d %H:%M:%S.%f",     # Standard format
            "%Y-%m-%d %H:%M:%S",        # Fallback: no microseconds
            "%Y-%m-%d"                  # Fallback: just date
        ]

        for fmt in formats_to_try:
            try:
                dt = datetime.strptime(value, fmt)
                return make_aware(dt)  # <== this makes it timezone-aware (uses Django timezone setting)

            except (ValueError, TypeError):
                continue

        # Still couldn't parse
        raise ValueError(f"Could not parse datetime: {value}")

class VehicleResource(resources.ModelResource):
    # id = fields.Field(attribute='id', column_name='Id')
    lot_id = fields.Field(attribute='lot_id', column_name='Lot number')
    vin = fields.Field(attribute='vin', column_name='VIN')
    auction_name = fields.Field(attribute='auction_name', column_name='Yard name')
    make = fields.Field(attribute='make', column_name='Make')
    model = fields.Field(attribute='model', column_name='Model Detail')
    year = fields.Field(attribute='year', column_name='Year')
    body_style = fields.Field(attribute='body_style', column_name='Body Style')
    car_keys = fields.Field(attribute='car_keys', column_name='Has Keys-Yes or No')
    color = fields.Field(attribute='color', column_name='Color')
    cylinders = fields.Field(attribute='cylinders', column_name='Cylinders')
    doc_type = fields.Field(attribute='doc_type', column_name='Sale Title Type')
    drive = fields.Field(attribute='drive', column_name='Drive')
    engine_type = fields.Field(attribute='engine_type', column_name='Engine')
    est_retail_value = fields.Field(attribute='est_retail_value', column_name='Est. Retail Value')
    fuel = fields.Field(attribute='fuel', column_name='Fuel Type')
    highlights = fields.Field(attribute='highlights', column_name='Special Note')
    location = fields.Field(attribute='location', column_name='Location city')
    odometer = fields.Field(attribute='odometer', column_name='Odometer')
    primary_damage = fields.Field(attribute='primary_damage', column_name='Damage Description')
    secondary_damage = fields.Field(attribute='secondary_damage', column_name='Secondary Damage')
    seller = fields.Field(attribute='seller', column_name='Seller Name')
    series = fields.Field(attribute='series', column_name='Trim')
    transmission = fields.Field(attribute='transmission', column_name='Transmission')
    vehicle_type = fields.Field(attribute='vehicle_type', column_name='Vehicle Type')
    is_insurance = fields.Field(attribute='is_insurance', column_name='Sealed=Vix')
    currency_code = fields.Field(attribute='currency_code', column_name='Currency Code')
    created_at = fields.Field(attribute='created_at', column_name='Create Date/Time' ,
        widget=FlexibleDateTimeWidget())
    updated_at = fields.Field(attribute='updated_at', column_name='Last Updated Time',
        widget=FlexibleDateTimeWidget())
    car_photo_urls = fields.Field(attribute='car_photo_urls', column_name='Image URL')
    damage_photos = fields.Field(attribute='damage_photos', column_name='Image Thumbnail')
    buy_now_price_histories = fields.Field(attribute='buy_now_price_histories', column_name='Buy-It-Now Price')
    active_bidding = fields.Field(attribute='active_bidding', column_name='Sale Status')
    buy_now_car = fields.Field(attribute='buy_now_car', column_name='Buy-It-Now Price')
    car_info = fields.Field(
        attribute='car_info',
        column_name='Model Group',  # Required but not actually used in widget
        widget=CarInfoCreateEveryTimeWidget()
    )

    class Meta:
        model = Vehicle
        import_id_fields = ['vin']  # Or 'lot_id' if that's unique
        skip_unchanged = True
        report_skipped = True


@admin.register(Vehicle)
class VehicleAdmin(ImportExportModelAdmin):
    change_list_template = "admin/vehicles/vehicle/change_list.html"

    resource_class = VehicleResource
    list_display = (
        'id', 'lot_id', 'vin', 'year', 'make', 'model', 'body_style',
        'color', 'drive', 'fuel', 'transmission', 'location', 'odometer',
        'primary_damage', 'secondary_damage', 'to_be_published', 'to_be_updated', 'created_at'
    )
    search_fields = ('vin', 'lot_id', 'make', 'model')
    list_filter = ('year', 'make', 'fuel', 'location', 'vehicle_type', 'to_be_updated', 'to_be_published')
    ordering = ('-id',)

