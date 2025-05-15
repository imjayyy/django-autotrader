from rest_framework import serializers
from .models import Fuel, BodyStyle, Transmission, Drive, Color, Status, Feature, Label, Make, Model, Vehicle, VehicleMedia
from shipping.models import Country


class FuelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fuel
        fields = '__all__'

class BodyStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyStyle
        fields = '__all__'

class TransmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transmission
        fields = '__all__'

class DriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drive
        fields = '__all__'

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = '__all__'

class MakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Make
        fields = '__all__'

class ModelSerializer(serializers.ModelSerializer):
    make = MakeSerializer()

    class Meta:
        model = Model
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class VehicleMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleMedia
        fields = ["vehicle_image_id", "img_url_from_api", "image_path", "video_path", "image"]

class MakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Make
        fields = ["id", "name"]

class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = ["id", "name"]

class VehicleSerializer(serializers.ModelSerializer):
    all_media = VehicleMediaSerializer(source="vehiclemedia_set", many=True, read_only=True)
    model = ModelSerializer()
    
    class Meta:
        model = Vehicle
        fields = ["id", "model", "year", "all_media"]

class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['id', 'name_az', 'name_en', 'color_hex', 'font_awesome_icon']


class VehicleListSerializer(serializers.ModelSerializer):
    all_media = VehicleMediaSerializer(source="vehiclemedia_set", many=True, read_only=True)
    model = ModelSerializer()
    make = MakeSerializer()
    fuel = FuelSerializer()
    body_style = BodyStyleSerializer()
    transmission = TransmissionSerializer()
    drive = DriveSerializer()
    color = ColorSerializer()
    status = StatusSerializer()
    feature_list = FeatureSerializer(many=True)
    label_list = LabelSerializer(many=True)

    country = CountrySerializer()
    class Meta:
        model = Vehicle
        fields = ["id", "make", "model", "fuel", "year", "price", 'price_discount', "status", "feature_list", "label_list",
                "transmission", "drive", "odometer", "body_style", "engine_type",
                "country", "all_media", "color", "engine_power", "engine_power_unit",
                 "zero_to_hundred", "motor_power", "motor_power_unit", "battery_range",     
                  ]



class VehicleDetailsSerializer(serializers.ModelSerializer):
    all_media = VehicleMediaSerializer(source="vehiclemedia_set", many=True, read_only=True)
    model = ModelSerializer()
    make = MakeSerializer()
    fuel = FuelSerializer()
    body_style = BodyStyleSerializer()
    transmission = TransmissionSerializer()
    drive = DriveSerializer()
    color = ColorSerializer()
    status = StatusSerializer()
    country = CountrySerializer()
    feature_list = FeatureSerializer(many=True, read_only=True)    
    label_list = LabelSerializer(many=True, read_only=True)
    class Meta:
        model = Vehicle
        fields = '__all__'