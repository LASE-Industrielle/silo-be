from django.db import models


class Silo(models.Model):
    title = models.CharField(max_length=200)


class Laser(models.Model):
    title = models.CharField(max_length=200)


class Measurement(models.Model):
    title = models.CharField(max_length=200)
