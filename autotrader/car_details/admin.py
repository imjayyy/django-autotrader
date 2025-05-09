from django.contrib import admin
from .models import Vehicle, Model, Make, VehicleMedia, Fuel, BodyStyle, Transmission, Drive, Color, Status, Feature, Label
from django import forms
# Register your models here.


class VehicleAdminForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set an empty queryset initially
        self.fields["model"].queryset = Model.objects.none()

        # When editing an existing Vehicle
        if self.instance.pk:
            self.fields["model"].queryset = Model.objects.filter(make=self.instance.make)
        
        # When adding a new Vehicle (Django Admin add form)
        elif "make" in self.data:
            try:
                make_id = int(self.data.get("make"))
                self.fields["model"].queryset = Model.objects.filter(make_id=make_id)
            except (ValueError, TypeError):
                self.fields["model"].queryset = Model.objects.none()  # Empty queryset if error

class VehicleAdmin(admin.ModelAdmin):
    form = VehicleAdminForm
    search_fields = ["make__name", "model__name", "year", "id"]
    list_filter = ('model', 'year')  # Fields to filter (will appear on right sidebar)
    list_display = ("id", "make", "model", "year", "price", "is_published")  # Fields to display in the list view

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "model" and "make" in request.GET:
            try:
                make_id = int(request.GET.get("make"))
                kwargs["queryset"] = Model.objects.filter(make_id=make_id)
            except (ValueError, TypeError):
                kwargs["queryset"] = Model.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ("admin/js/vehicle_admin.js",)  # Include custom JavaScript file



class ModelAdmin(admin.ModelAdmin):
    list_filter = ['make']  # Fix reference to 'make' (not 'make')
    search_fields = ['name']
    ordering = ['name']

class MakeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering = ['name']

class VehicleMediaAdmin(admin.ModelAdmin):
    autocomplete_fields = ['vehicle']

# Register models in the Django admin panel


admin.site.register(Model, ModelAdmin)
admin.site.register(Make, MakeAdmin)
admin.site.register(Vehicle, VehicleAdmin)

admin.site.register(VehicleMedia, VehicleMediaAdmin)
admin.site.register(Fuel)
admin.site.register(BodyStyle)
admin.site.register(Transmission)
admin.site.register(Drive)
admin.site.register(Color)
admin.site.register(Status)
admin.site.register(Feature)
admin.site.register(Label)