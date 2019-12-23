from django.contrib import admin
# Register your models here.
from django.contrib.auth.models import User

from api.models import Silo, Sensor, Measurement, Notification

admin.site.register(Silo)
admin.site.register(Notification)


@admin.register(Measurement)
class MeasurementModelAdmin(admin.ModelAdmin):
    list_display = ('value', 'saved', 'sensor', 'sensor_timestamp', 'temperature', 'humidity', 'pressure', 'acc')


@admin.register(Sensor)
class SensorModelAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(is_superuser=False)
        return super(SensorModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
