# context_processors.py
from shipping.models import Country

def menu_items(request):
    return {
        'countries': Country.objects.all()
    }
