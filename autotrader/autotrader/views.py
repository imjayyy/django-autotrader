from django.shortcuts import render

def home(request):
    return render(request, 'home.html')


def search_results(request):
    return render(request, 'search-results.html')


def search_filter(request):
    return render(request, 'search-filter.html')


def car_details(request):
    return render(request, 'car-details.html')


def customs_calculator(request):
    return render(request, 'customs-calculator.html')

def about_us(request):
    return render(request, 'about-us.html')


def order_shipping(request):
    return render(request, 'order-shipping.html')


def normal_car_details(request):
    return render(request, 'normal-car-details.html')