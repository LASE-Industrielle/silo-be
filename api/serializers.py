from rest_framework import serializers

from api import models


class SiloSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'title',
        )
        model = models.Silo


class LaserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'title',
        )
        model = models.Laser


class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'title',
        )
        model = models.Measurement
