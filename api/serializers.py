from rest_framework import serializers

from api import models


class SiloSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'title',
        )
        model = models.Silo


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'title',
        )
        model = models.Sensor


class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'title',
        )
        model = models.Measurement
