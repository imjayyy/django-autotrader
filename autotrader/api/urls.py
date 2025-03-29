
from django.urls import path, include
from .views import get_car_models, get_car_models_from_id, search_api

urlpatterns = [
    path('models/<str:make>/', get_car_models, name='get_car_models'),
    path('models-from-id/', get_car_models_from_id, name='get_car_models_from_id'),
    path('search-api/', search_api, name='search_api'),
]
