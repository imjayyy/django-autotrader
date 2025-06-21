from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Vehicle

class CarSitemap(Sitemap):
    def items(self):
        # Return all vehicles without pagination
        return Vehicle.objects.all()

    def location(self, obj):
        # URL for each vehicle detail page
        return reverse('car_details', args=[obj.id])

    def lastmod(self, obj):
        # Last modification date for the vehicle
        return obj.updated_at

    def count(self):
        # Total count of vehicles (this is optional but may be helpful for the sitemap index)
        return Vehicle.objects.count()
