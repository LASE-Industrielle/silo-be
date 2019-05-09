from django.contrib import admin

# Register your models here.
from api.models import Silo, Sensor, Measurement

admin.site.register(Silo)
admin.site.register(Sensor)
admin.site.register(Measurement)
