# from django.contrib import admin
# from .models import AuctionVehicle, AuctionCurrency, AuctionActiveBid
# from django import forms
# from django.utils.translation import gettext_lazy as _
# Register your models here.


from django.contrib import admin
from .models import AuctionDetail, AuctionActiveBid, AuctionCurrency, Auction, BuyNowPriceHistory
from .models import AuctionVehicle as Vehicle
from .models import AuctionVehicleMedia as VehicleMedia
from car_details.models import Make, Model, Fuel, BodyStyle, Transmission, Drive, Color, Country, Status
import requests
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.timezone import make_aware
import datetime
from urllib.parse import urlencode, parse_qs, urlparse, urlunparse
from .map_data import map_api_data_to_auction_data, map_response_to_models_single_vehicle
from django.shortcuts import render




@admin.register(AuctionDetail)
class AuctionDetailsAdmin(admin.ModelAdmin):
    list_display = ['auctionvehicle', 'lot_number', 'get_auction_name', 'location', 'created_at']
    change_list_template = "admin/auction_api/auctionvehicle_changelist.html"

    def get_auction_name(self, obj):   
        return obj.auction.auction_name

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-auctions/', self.admin_site.admin_view(self.import_auction_data), name='import-auctions'),

        ]
        return custom_urls + urls

    def import_auction_data(self, request):
        query_string = request.META['QUERY_STRING']
        # Step 2: Construct the API URL with the full query string
        api_url = f"https://copart-iaai-api.com/api/v2/get-active-lots?{query_string}"
        query_params = parse_qs(request.META['QUERY_STRING'])
        page = int(query_params.get('page', [1])[0])
        per_page = int(query_params.get('per_page', [50])[0])
        max_pages = 10
        # --- Parse and save vehicle and auction models ---
        for current_page in range(page, page + max_pages):
            query_params['page'] = [str(current_page)]
            full_query = urlencode(query_params, doseq=True)
            api_url = f"https://copart-iaai-api.com/api/v2/get-active-lots?{full_query}"
            response = requests.post(api_url)
            data = response.json()
            max_pages = data.get('pagination').get('total_pages')
            auction_list = data['result']  # one record or loop if list
            for auction in auction_list:
                try:
                    map_api_data_to_auction_data(auction)
                except Exception as e:
                    self.message_user(request, f"Error: {e}", messages.ERROR)
        self.message_user(request, "Auction data imported successfully", messages.SUCCESS)
        return redirect("..")


@admin.register(Vehicle)
class AuctionVehicleAdmin(admin.ModelAdmin):
    list_display = ['make', 'model', 'VIN']
    change_list_template = "admin/auction_api/update_single_vehicle.html"  # custom form template

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('update-single-vehicle/', self.admin_site.admin_view(self.update_single_vehicle), name='update-single-vehicle'),
        ]
        return custom_urls + urls

    def update_single_vehicle(self, request):
        if request.method == 'GET' and 'api_token' in request.GET and 'vin_number' in request.GET:
            api_token = request.GET['api_token']
            vin = request.GET['vin_number']
            only_with_color = request.GET.get('only_with_color', 0)

            query = urlencode({
                'api_token': api_token,
                'vin_number': vin,
                'only_with_color': only_with_color
            })
            print(f"Query: {query}")  # Debugging line to check the query string

            api_url = f"https://copart-iaai-api.com/api/v1/get-car-vin?{query}"
            response = requests.post(api_url)
            data = response.json()
            if 'result' in data:
                auction_data = data['result']
                map_response_to_models_single_vehicle(data)
                self.message_user(request, f"Vehicle with VIN {vin} updated successfully!", messages.SUCCESS)
            else:
                self.message_user(request, "No vehicle data returned from API.", messages.ERROR)        
            # try:
            #     response = requests.post(api_url)
            #     data = response.json()

            #     if 'result' in data:
            #         auction_data = data['result']
            #         map_response_to_models_single_vehicle(data)
            #         self.message_user(request, f"Vehicle with VIN {vin} updated successfully!", messages.SUCCESS)
            #     else:
            #         self.message_user(request, "No vehicle data returned from API.", messages.ERROR)

            # except Exception as e:
            #     self.message_user(request, f"Error updating vehicle: {e}", messages.ERROR)

            return redirect("..")

        # Show the form if method is GET without params
        return render(request, "admin/auction_api/vehicle_changelist.html")

admin.site.register(AuctionActiveBid)
admin.site.register(AuctionCurrency)
admin.site.register(VehicleMedia)


