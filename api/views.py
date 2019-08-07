# Create your views here.
import csv
import datetime

from django.db.models import Max
from django.db.models.functions import Trunc
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
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


def measures_for_graph(request, sensor_id, timespan_type):
    # Replacement for SWITCH, dictionary with lambdas that will be executed only when the proper call is made
    # otherwise it will return empty json
    return {
        'day': lambda s_id: _measures_by_day(s_id),
        'hour': lambda s_id: _measures_by_hour(s_id),
        'week': lambda s_id: _measures_by_week(s_id),
        'month': lambda s_id: _measures_by_month(s_id)
    }.get(timespan_type, lambda s_id: JsonResponse({}))(sensor_id)


def _measures_by_hour(sensor_id):
    # get maximum dates grouped by expected time format (in this case hours and minutes)
    delta = timezone.timedelta(hours=1)
    truncated_timestamp = Trunc('saved', 'minute', tzinfo=timezone.utc)
    key_format = "%H:%M"
    return _get_measures_as_json_response(delta, key_format, sensor_id, truncated_timestamp)


def _measures_by_day(sensor_id):
    delta = timezone.timedelta(days=1)
    truncated_timestamp = Trunc('saved', 'hour', tzinfo=timezone.utc)
    key_format = "%H:00"

    return _get_measures_as_json_response(delta, key_format, sensor_id, truncated_timestamp)


def _measures_by_week(sensor_id):
    delta = timezone.timedelta(weeks=1)
    key_format = "%d.%m"
    truncated_timestamp = Trunc('saved', 'day', tzinfo=timezone.utc)

    return _get_measures_as_json_response(delta, key_format, sensor_id, truncated_timestamp)


def _measures_by_month(sensor_id):
    delta = timezone.timedelta(days=30)
    key_format = "%d.%m"
    truncated_timestamp = Trunc('saved', 'day', tzinfo=timezone.utc)

    return _get_measures_as_json_response(delta, key_format, sensor_id, truncated_timestamp)


def _get_measures_as_json_response(delta, key_format, sensor_id, truncated_timestamp):
    now = timezone.now()
    filter_from = now - delta
    base_query = Measurement.objects.filter(sensor_id=sensor_id, saved__gte=filter_from, saved__lte=now)
    measure_dates = base_query.annotate(saved_trunc=truncated_timestamp).values('saved_trunc').annotate(
        max_date=Max('saved'))
    max_value_dates = [m['max_date'] for m in measure_dates]
    measures = Measurement.objects.filter(sensor_id=sensor_id, saved__in=max_value_dates).order_by('saved')
    result = {}
    for m in measures:
        result[m.saved.strftime(key_format)] = m.value
    return JsonResponse(result)


def export_measures_for_sensor(request, sensor_id):
    measures = Measurement.objects.filter(sensor=sensor_id).all()
    time_format_filename = "%Y-%m-%d-%H-%M-%S"
    time_format_in_csv = "%Y-%m-%d %H:%M:%S"
    exported_at = datetime.datetime.now().strftime(time_format_filename)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="measurements_{exported_at}.csv"'
    writer = csv.writer(response)

    for measure in measures:
        writer.writerow([measure.saved.strftime(time_format_in_csv), measure.value])

    return response
