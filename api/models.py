from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class Sensor(models.Model):
    serial_number = models.CharField(max_length=200, default='')
    type = models.CharField(max_length=200, default='LASER')


class Silo(models.Model):
    height = models.FloatField(default=0)
    width = models.FloatField(default=0)
    capacity = models.FloatField(default=0)
    percentage = models.FloatField(default=0)
    location = models.CharField(max_length=400, null=True, blank=True)
    sensor = models.ForeignKey(Sensor, null=True, on_delete=models.CASCADE)


class Measurement(models.Model):
    value = models.FloatField(default=0)
    read = models.DateTimeField(null=True)
    saved = models.DateTimeField(auto_now_add=True, null=True)
    sensor = models.ForeignKey(Silo, on_delete=models.PROTECT, blank=True, null=True)


# Automatically creates and saves the token for every newly registered user
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
