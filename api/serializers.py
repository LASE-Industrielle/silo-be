from rest_framework import serializers

from api import models



class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sensor
        fields = '__all__'


class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Measurement
        fields = '__all__'


class SiloSerializer(serializers.ModelSerializer):
    sensor = SensorSerializer()
    class Meta:
        model = models.Silo
        fields = '__all__'
