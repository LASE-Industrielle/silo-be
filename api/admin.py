from django.contrib import admin

# Register your models here.
from api.models import Silo, Sensor, Measurement

admin.site.register(Silo)
admin.site.register(Sensor)


@admin.register(Measurement)
class MeasurementModelAdmin(admin.ModelAdmin):
    list_display = ('value', 'saved', 'sensor')
