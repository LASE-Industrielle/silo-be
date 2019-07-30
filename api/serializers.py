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
    values_by_day = serializers.SerializerMethodField()
    last_update = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = models.Silo
        fields = '__all__'

    def get_values_by_day(self, obj):
        return obj.values_by_day()

    def get_last_update(self, obj):
        return obj.last_update()

    def get_percentage(self, obj):
        return obj.percentage()


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Notification
        fields = '__all__'
