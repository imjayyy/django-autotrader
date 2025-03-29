from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Vehicle
from .serializers import VehicleSerializer
# Create your views here.


from django.http import JsonResponse
from .models import Model

def get_models(request):
    make_id = request.GET.get("make_id")
    models = Model.objects.filter(make_id=make_id).values("id", "name")
    return JsonResponse({"models": list(models)})
