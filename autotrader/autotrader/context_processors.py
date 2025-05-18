# context_processors.py
from shipping.models import Country
from general.models import Information, InformationSerializer



def menu_items(request):
    return {
        'countries': Country.objects.all()
    }

def get_notifications(request):
    
    information = Information.objects.all().order_by('-updated_at')[:3]
    information_serializer = InformationSerializer(information, many=True)

    return {
        'notifications': information_serializer.data
    }