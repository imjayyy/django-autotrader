# auction_api/models.py
from django.db import models
from car_details.models import Make, Model, Fuel, BodyStyle, Transmission, Drive, Color, Country, Status, Feature, Label, VehicleMedia
from tinymce.models import HTMLField


class AuctionCurrency(models.Model):
    name = models.CharField(max_length=100)
    char_code = models.CharField(max_length=10)
    iso_code = models.IntegerField()
    code_id = models.IntegerField()

    def __str__(self):
        return self.name


class AuctionActiveBid(models.Model):
    auction = models.IntegerField()
    all_lots_id = models.BigIntegerField()
    sale_date = models.BigIntegerField()  # JavaScript timestamp
    current_bid = models.FloatField()
    date_updated = models.BigIntegerField()
    bid_updated = models.BigIntegerField()

    def __str__(self):
        return f"Auction {self.auction} for Lot {self.all_lots_id}"


class AuctionVehicle(models.Model):
    make = models.ForeignKey(Make, on_delete=models.CASCADE)
    model = models.ForeignKey(Model, on_delete=models.CASCADE)
    fuel = models.ForeignKey(Fuel, null=True, on_delete=models.CASCADE)
    body_style = models.ForeignKey(BodyStyle, null=True,  on_delete=models.CASCADE)
    transmission = models.ForeignKey(Transmission, null=True, on_delete=models.CASCADE)
    drive = models.ForeignKey(Drive, null=True, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, null=True, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, null=True,  on_delete=models.CASCADE)
    cylinders = models.IntegerField(blank=True, null=True)
    status = models.ForeignKey(Status, null=True, on_delete=models.CASCADE)
    feature_list =  models.ManyToManyField(Feature, null=True, related_name='feature_list_auction_vehicles')
    label_list = models.ManyToManyField(Label, null=True,  related_name='label_list_auction_vehicles')
    odometer = models.IntegerField(null=True )
    zero_to_hundred = models.DecimalField(blank=True, null=True, decimal_places=1, max_digits=5 )
    motor_power = models.IntegerField(blank=True, null=True)
    motor_power_unit = models.CharField(max_length=50, blank=True, null=True)
    battery_range = models.IntegerField(blank=True, null=True)
    year = models.IntegerField()
    engine_power_unit = models.CharField(max_length=50,blank=True, null=True)
    engine_power = models.IntegerField(blank=True, null=True)
    engine_type = models.CharField(max_length=50,blank=True, null=True)
    comment = HTMLField(blank=True, null=True)
    VIN = models.TextField(blank=True, null=True)
    currency = models.TextField(null=True, )
    price_discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price = models.FloatField(null=True )
    number_of_seats = models.IntegerField(null=True)
    is_published = models.BooleanField(default=True)
    documents = models.TextField(blank=True, null=True)
    is_popular = models.BooleanField(default=False)
    supplier_id = models.BigIntegerField(blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True)
    to_be_updated = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.model} ({self.year})"

class Auction(models.Model):
    auction_name = models.CharField(max_length=255)
    auction_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.auction_name

class BuyNowPriceHistory(models.Model):
    auctionvehicle = models.ForeignKey(AuctionVehicle, on_delete=models.CASCADE, related_name='buy_now_price_history')
    price = models.FloatField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Buy Now Price for {self.auctionvehicle} - {self.price}"


class AuctionDetail(models.Model):
    auctionvehicle = models.ForeignKey(AuctionVehicle, on_delete=models.CASCADE, related_name='auction_vehicles')
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='auction_details')
    lot_number = models.BigIntegerField()
    car_keys = models.CharField(max_length=20, blank=True, null=True)
    primary_damage = models.CharField(max_length=100, blank=True, null=True)
    secondary_damage = models.CharField(max_length=100, blank=True, null=True)
    highlights = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255)
    est_retail_value = models.FloatField(blank=True, null=True)
    is_insurance = models.BooleanField(null=True)
    doc_type = models.CharField(max_length=100, blank=True, null=True)
    vin = models.CharField(max_length=100)
    created_at = models.DateTimeField()

    # Connect to VehicleMedia via reverse FK from VehicleMedia.all_lots_id
    damage_photos = models.JSONField(blank=True, null=True)
    car_info = models.JSONField(blank=True, null=True)
    sales_history_last = models.JSONField(blank=True, null=True)
    sales_history = models.JSONField(blank=True, null=True)
    active_bidding = models.ManyToManyField(AuctionActiveBid, blank=True)
    buy_now_car = models.JSONField(blank=True, null=True)

    currency = models.ForeignKey(AuctionCurrency, on_delete=models.SET_NULL, null=True, blank=True)

    sale_date = models.DateTimeField(blank=True, null=True)  # JavaScript timestamp
    sale_status = models.CharField(max_length=50, blank=True, null=True)  # e.g., "sold", "available"
    purchase_price = models.FloatField(blank=True, null=True)
    buyer_country = models.CharField(max_length=50, blank=True, null=True) 

    def __str__(self):
        return f"AuctionVehicle Lot {self.lot_number} - {self.auctionvehicle.model}"

    @property
    def car_photos(self):
        return VehicleMedia.objects.filter(all_lots_id=self.lot_number)



def vehicle_image_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    # Use a temp name until we get the ID
    return f"vehicles/temp.{ext}"

class AuctionVehicleMedia(models.Model):
    vehicle_image_id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='vehicles/', null=True, blank=True) 
    api_id = models.IntegerField(null=True, blank=True)
    all_lots_id = models.BigIntegerField(null=True, blank=True)
    vin = models.TextField(null=True, blank=True)
    img_url_from_api = models.TextField(null=True, blank=True)
    vehicle = models.ForeignKey(AuctionVehicle, on_delete=models.CASCADE)
    image_path = models.CharField(null=True, blank=True, max_length=255)
    video_path = models.CharField(null=True, blank=True, max_length=255)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new and self.image:
            # Now rename the image to vehicle_image_id
            ext = os.path.splitext(self.image.name)[1]
            new_name = f"vehicles/{self.vehicle_image_id}{ext}"
            from django.core.files.storage import default_storage
            old_image = self.image
            new_image = default_storage.save(new_name, old_image)
            self.image.name = new_name
            super().save(update_fields=['image'])

    def __str__(self):
        return f"VehicleMedia {self.vehicle_image_id} - VIN: {self.vin}"

