# vehicles/apps.py
from django.apps import AppConfig
import os

class VehiclesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vehicles'

    def ready(self):
        # Prevent double initialization caused by Django autoreloader
        if os.environ.get("RUN_MAIN") == "true":
            
            from .scheduler import start_scheduler
            start_scheduler()

# import os
# import threading
# from django.apps import AppConfig

# class VehiclesConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'vehicles'

#     def ready(self):
#         if os.environ.get("RUN_MAIN") == "true":
#             from vehicles.models import Vehicle
#             from vehicles.services import fetch_car_vin_data
#             from .scheduler import start_scheduler

#             def run_vin_update():
#                 if Vehicle.objects.filter(to_be_updated=True, vin__isnull=False).exists():
#                     fetch_car_vin_data()
#                 else:
#                     print("[INFO] No vehicles to update.")

#             # Run VIN fetch in a background thread
#             threading.Thread(target=run_vin_update).start()

#             # Start any scheduled jobs too
#             start_scheduler()
