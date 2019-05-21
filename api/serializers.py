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
    last_days_in_average = serializers.SerializerMethodField()

    class Meta:
        model = models.Silo
        fields = '__all__'

    def get_last_days_in_average(self, obj):
        return obj.last_days_in_average()
