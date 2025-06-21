from django.urls import path
from .views import *
from .sitemaps import CarSitemap
from django.contrib.sitemaps.views import sitemap

sitemaps = {
    'vehicle': CarSitemap,
}

urlpatterns = [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),

    path('', index, name='index'),
    path('get-filtered-options/', get_filtered_options, name='get_filtered_options'),


    path('admin-fetch-vehicles-form/', vechile_api_manual_form, name='vechile_api_manual_form'),

    ################# TEST VECHILE VIN ###########################
    # path('test_vechile_vin/', test_vechile_vin, name='test_vechile_vin'),

    # path('process_and_print_hello/', process_and_print_hello, name='process_and_print_hello'),
    
    path('admin-fetch-vehicles-vin-form/', vechile_get_vin_manual_form, name='vechile_get_vin_manual_form'),

    
    path('trigger_vechile_vin/', trigger_vechile_vin, name='trigger_vechile_vin'),

    path('auction-car-details/<int:id>/', car_details, name='auction_car_details'),

    path('get-models-by-make/', get_models_by_make, name='get_models_by_make'),

    path('contact/', contact_us, name='contact_us'),

    path('search/', vehicle_list, name='search'),

    path('upload-csv/', upload_csv, name='upload_csv'),

    
    path('vehicle-search/', vehicle_search_api, name='vehicle_search_api'),
    


    
]