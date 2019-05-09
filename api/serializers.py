from rest_framework import serializers

from api import models


class SiloSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Silo
        fields = '__all__'


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sensor
        fields = '__all__'


class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Measurement
        fields = '__all__'
