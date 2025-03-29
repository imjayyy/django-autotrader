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

urlpatterns = [
    path('', views.home, name='home'),
    path('search-results', views.search_results, name='search-results'),
    path('search-filter', views.search_filter, name='search-filter'),
    path('car-details', views.car_details, name='car-details'),
    path('customs-calculator', views.customs_calculator, name='customs-calculator'),
    path('about-us', views.about_us, name='about-us'),
    path('order-shipping', views.order_shipping, name='order-shipping'),
    path('normal-car-details/<id>', views.normal_car_details, name='normal-car-details'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),

]

urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),  # Language switcher
]

urlpatterns += [
    path('api/', include('api.urls')),
]


urlpatterns += [
    path("admin-api/get-models/", get_models, name="get-models"),
]

# urlpatterns += i18n_patterns(
#     path('admin/', admin.site.urls)

# )
