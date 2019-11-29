from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db import models
from django.db.models import Max
from django.db.models.functions import TruncDay
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class Sensor(models.Model):
    serial_number = models.CharField(max_length=200, default='')
    type = models.CharField(max_length=200, default='LASER')

    def __str__(self):
        return self.type + " (" + self.serial_number + ")"


class Silo(models.Model):
    name = models.CharField(max_length=200, default="")
    height = models.FloatField(default=0)
    width = models.FloatField(default=0)
    capacity = models.FloatField(default=0)
    location = models.CharField(max_length=400, null=True, blank=True)
    sensor = models.ForeignKey(Sensor, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def last_update(self):
        last_measure = Measurement.objects.filter(sensor=self.sensor).order_by('-saved').first()
        if last_measure is None:
            return "no measures"
        result = naturaltime(last_measure.saved)

        result = result.replace("minutes", "m")
        result = result.replace("minute", "m")
        result = result.replace("hours", "h")
        result = result.replace("hour", "h")
        result = result.replace("days", "d")
        result = result.replace("day", "d")
        result = result.replace("weeks", "w")
        result = result.replace("week", "w")
        result = result.replace("months", "mo")
        result = result.replace("month", "mo")
        result = result.replace("years", "y")
        result = result.replace("year", "y")

        return result

    def values_by_day(self):
        measures = Measurement.objects.filter(sensor=self.sensor).annotate(day=TruncDay('saved')).values(
            'day').annotate(max=Max('saved')).values('day', 'max').order_by('-day')[1:4]

        averages = {}
        for measure in measures:
            latest = Measurement.objects.filter(sensor=self.sensor, saved=measure['max']).first()
            averages[measure['day'].strftime('%Y-%m-%d')] = latest.value

        return averages

    def percentage(self):
        last_measure = Measurement.objects.filter(sensor=self.sensor).order_by('-saved').first()
        if last_measure is None:
            return "N/A"
        return last_measure.value


class Measurement(models.Model):
    value = models.FloatField(default=0)
    read = models.DateTimeField(null=True)
    saved = models.DateTimeField(auto_now_add=True, null=True)
    sensor = models.ForeignKey(Sensor, on_delete=models.PROTECT, blank=True, null=True)
    sensor_timestamp = models.CharField(max_length=15, default='')
    temperature = models.FloatField(default=0)
    humidity = models.FloatField(default=0)
    pressure = models.FloatField(default=0)
    acc = models.CharField(max_length=30, default='')

    def __str__(self):
        return str(self.value) + " - " + str(self.saved)


class Notification(models.Model):
    title = models.CharField(max_length=100, default="")
    body = models.CharField(max_length=200, default="")
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Title: {self.title} | Body: {self.body} | Timestamp: {self.timestamp}"


# Automatically creates and saves the token for every newly registered user
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
