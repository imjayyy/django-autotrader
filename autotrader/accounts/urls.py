from django.urls import path
from .views import auth_view, logout_view, create_order

urlpatterns = [
    path('login/', auth_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('order-now/', create_order, name='order_now'),
]
