from django.contrib import admin

# Register your models here.
from api.models import Silo, Sensor, Measurement, Notification

admin.site.register(Silo)
admin.site.register(Sensor)
admin.site.register(Notification)


@admin.register(Measurement)
class MeasurementModelAdmin(admin.ModelAdmin):
    list_display = ('value', 'saved', 'sensor', 'sensor_timestamp', 'temperature', 'humidity', 'pressure', 'acc')
