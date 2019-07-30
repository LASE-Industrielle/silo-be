# Create your views here.
from datetime import datetime

from django.http import JsonResponse
from fcm_django.fcm import fcm_send_topic_message
from rest_framework import viewsets, status
from rest_framework.response import Response

from api import models, serializers
from api.models import Measurement, Notification, Silo


class SiloViewSet(viewsets.ModelViewSet):
    queryset = models.Silo.objects.all()
    serializer_class = serializers.SiloSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = models.Notification.objects.all().order_by("-timestamp")
    serializer_class = serializers.NotificationSerializer


class SensorViewSet(viewsets.ModelViewSet):
    queryset = models.Sensor.objects.all()
    serializer_class = serializers.SensorSerializer


class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = models.Measurement.objects.all()
    serializer_class = serializers.MeasurementSerializer
    critical_levels = [20, 40, 60, 80]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        latest_measurement = Measurement.objects.filter(sensor=serializer.validated_data["sensor"]).latest("id").value
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        silo = Silo.objects.filter(sensor=serializer.data["sensor"]).first()
        for level in self.critical_levels:
            if serializer.data["value"] < level <= latest_measurement:
                self.send_notification(silo.name, level)
                break

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @staticmethod
    def send_notification(silo_name, level):
        title = silo_name
        body = f"The level is below {level}%"
        notification = Notification(title=title, body=body)
        notification.save()
        fcm_send_topic_message(topic_name='silo1', sound='default', message_body=body, message_title=title,
                               data_message={"body": body, "title": title})


def all_measures_for_sensor(request, sensor_id):
    measures = Measurement.objects.filter(sensor=sensor_id).order_by('-saved').all()

    result = {}

    for measure in measures:

        measure_date = measure.saved.strftime('%Y-%m-%d')
        measure_day = measure.saved.strftime('%d')
        measure_month = measure.saved.strftime('%m')
        measure_year = measure.saved.strftime('%Y')

        if result.get(measure_date) is None:  # don't fetch them again
            measures_per_day_objects = Measurement.objects.filter(sensor=sensor_id,
                                                                  saved__day=measure_day,
                                                                  saved__month=measure_month,
                                                                  saved__year=measure_year).order_by('-saved')

            measures_per_day = {m.saved.strftime('%H:%M'): m.value for m in measures_per_day_objects}
            result[measure_date] = measures_per_day

    return JsonResponse(result)
