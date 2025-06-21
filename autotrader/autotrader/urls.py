"""
URL configuration for autotrader project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from car_details.views import get_models
from django.conf import settings
from django.conf.urls.static import static
from vehicles.urls import urlpatterns as vehicles_urls

urlpatterns = [
    path('', views.home, name='home'),
    path('search-results', views.search_results, name='search-results'),
    path('search-filter', views.search_filter, name='search-filter'),
    path('car-details', views.car_details, name='car-details'),
    path('contact', views.contact, name='contact'),
    path('customs-calculator', views.customs_calculator, name='customs-calculator'),
    path('about-us', views.about_us, name='about-us'),
    path('order-shipping', views.order_shipping, name='order-shipping'),
    path('normal-car-details/<id>', views.normal_car_details, name='normal-car-details'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('text-search/', views.text_search, name='text-search'),
    path('information', views.information, name='information'),
    path('information-view/<int:id>/', views.information_view, name='information-view'),
    path('create-order/<int:id>/', views.create_order, name='create-order'),
    path('form-submission/', views.form_submission, name='form-submission'),
    path('auction_vehicle_search_results/', views.auction_vehicle_search_results, name='auction-vehicle-search-results'),
]

urlpatterns += vehicles_urls  # Include vehicle-related URLs

urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),  # Language switcher
]

urlpatterns += [
    path('api/', include('api.urls')),
]


urlpatterns += [
    path("admin-api/get-models/", get_models, name="get-models"),
]

urlpatterns += [
path('djrichtextfield/', include('djrichtextfield.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += i18n_patterns(
#     path('admin/', admin.site.urls)

# )
