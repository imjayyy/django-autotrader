from django.contrib import admin

# Register your models here.

from .models import Order, Callback, Information


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'vehicle', 'order_date', 'status')
    list_filter = ('status',)
    search_fields = ('customer__first_name', 'vehicle__make__name', 'vehicle__model__name')
    ordering = ('-order_date',)
    date_hierarchy = 'order_date'


class CallbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country_code', 'phone', 'created_at')
    search_fields = ('name', 'country_code', 'phone')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

class InformationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'updated_at')
    search_fields = ('title',)
    ordering = ('-updated_at',)
    date_hierarchy = 'updated_at'



admin.site.register(Information, InformationAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Callback, CallbackAdmin)