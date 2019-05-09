from django.contrib import admin

# Register your models here.
from api.models import Silo, Laser, Measurement

admin.site.register(Silo)
admin.site.register(Laser)
admin.site.register(Measurement)
