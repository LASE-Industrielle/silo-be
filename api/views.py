# Create your views here.
import csv

from dateutil import parser
from django.contrib.auth.models import User
from django.db.models import Max
from django.db.models.functions import Trunc
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.timezone import localtime
from fcm_django.fcm import fcm_send_topic_message
from pyfcm.errors import AuthenticationError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from math import pow, pi

from api import models, serializers
from api.models import Measurement, Notification, Silo, Sensor

SAVED_ASC = 'saved'
SAVED_DESC = '-saved'

HOUR = 'hour'
DAY = 'day'
WEEK = 'week'
MONTH = 'month'

KEY_FORMATS = {
    HOUR: "%H:%M",
    DAY: "%H:00",
    WEEK: "%d.%m",
    MONTH: "%d.%m"
}

TRUNCATION = {
    HOUR: Trunc('saved', 'minute', tzinfo=timezone.utc),
    DAY: Trunc('saved', HOUR, tzinfo=timezone.utc),
    WEEK: Trunc('saved', DAY, tzinfo=timezone.utc),
    MONTH: Trunc('saved', DAY, tzinfo=timezone.utc)
}

DELTAS = {
    HOUR: timezone.timedelta(hours=1),
    DAY: timezone.timedelta(days=1),
    WEEK: timezone.timedelta(weeks=1),
    MONTH: timezone.timedelta(days=30)
}


def _filter_queryset_by_user_permission(request, queryset):
    '''
    Narrow down showing resources to superusers and users that are assigned to the sensor
    :param request: request to get authenticated user
    :param queryset: base query set which is fetching all the resources
    :return:
    '''

    user: User = request.user
    if user.is_superuser:
        return queryset
    return queryset.filter(sensor__user__username=user.username)


class SiloViewSet(viewsets.ModelViewSet):
    queryset = models.Silo.objects.all().order_by("name")
    serializer_class = serializers.SiloSerializer

    def filter_queryset(self, queryset):
        return _filter_queryset_by_user_permission(self.request, queryset)


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = models.Notification.objects.all().order_by("-timestamp")
    serializer_class = serializers.NotificationSerializer

    def filter_queryset(self, queryset):
        user: User = self.request.user
        if user.is_superuser:
            return queryset
        silo = Silo.objects.filter(sensor__user__username=user.username).first()
        return queryset.filter(title=silo.name)


class SensorViewSet(viewsets.ModelViewSet):
    queryset = models.Sensor.objects.all()
    serializer_class = serializers.SensorSerializer


class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = models.Measurement.objects.all()
    serializer_class = serializers.MeasurementSerializer
    critical_levels = [20, 40, 60, 80]

    def filter_queryset(self, queryset):
        return _filter_queryset_by_user_permission(self.request, queryset)

    def _send_notifications_if_necessary(self, user, serializer):
        '''
        Check if sending notification is necessary,
        It will be triggered when value drops below the critical levels and the notification hasn't been sent already
        :param serializer:
        :return:
        '''
        sensor = serializer.validated_data["sensor"]
        silo = Silo.objects.filter(sensor=sensor).first()
        # getting the second latest measurement because the new measurement gets saved before this
        latest_measurement = Measurement.objects.filter(sensor=sensor).order_by("-id")[1].value
        for level in self.critical_levels:
            if serializer.validated_data["value"] < level <= latest_measurement:
                try:
                    self.send_notification(silo.name, level, topic=user.username)
                except AuthenticationError as e:
                    print("Sending notification ERROR, " + str(e))
                break

    def _user_is_allowed_to_create_measurement(self, user, sensor):
        '''
        Allow superusers to create measurement for all sensors, while other users can create measurement only
        for sensors they are assigned to
        :param sensor:
        :return:
        '''
        return user.is_superuser or (sensor.user and sensor.user.id == user.id)

    def create(self, request, *args, **kwargs):
        '''
        Create measurements in several steps:
        - validate the request
        - check if user is allowed to create measurement (if not, raise permission exception)
        - calculate percentage
        - create measurement
        - check if notification needs to be sent
        :param request:
        :param args:
        :param kwargs:
        :return:
        '''

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sensor: Sensor = serializer.validated_data["sensor"]
        distance = serializer.validated_data["value"]
        user: User = self.request.user

        silo = Silo.objects.filter(sensor=sensor).first()

        if silo:
            if silo.width is not None and silo.width > 0 and silo.height is not None and silo.height > 0:
                radius = silo.width / 2
                capacity = pi * pow(radius, 2) * (silo.height - silo.gap_top - silo.gap_bottom)
                content = pi * pow(radius, 2) * (silo.height - silo.gap_top - silo.gap_bottom - distance / 1000)
                percentage = content / capacity * 100

                serializer.validated_data["value"] = round(percentage, 2)
                serializer.validated_data["distance"] = distance
                serializer.validated_data["capacity"] = round(capacity, 2)
                serializer.validated_data["content"] = round(content, 2)
                serializer.validated_data["radius"] = radius
                serializer.validated_data["silo_height"] = silo.height
                serializer.validated_data["silo_width"] = silo.width
                serializer.validated_data["silo_gap_top"] = silo.gap_top
                serializer.validated_data["silo_gap_bottom"] = silo.gap_bottom

        if self._user_is_allowed_to_create_measurement(user, sensor):
            self.perform_create(serializer)

            self._send_notifications_if_necessary(user, serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            raise PermissionDenied(
                {"message": "You don't have write permission for this sensor", "sensor_id": sensor.id})

    @staticmethod
    def send_notification(silo_name, level, topic):
        title = silo_name
        body = f"The level is below {level}%"
        notification = Notification(title=title, body=body)
        notification.save()

        fcm_send_topic_message(topic_name=topic, sound='default', message_body=body, message_title=title,
                               data_message={"body": body, "title": title})

    @action(methods=['get'], detail=False, url_path='all/(?P<silo_id>[^/.]+)')
    def all_values_for_silo(self, request, silo_id):
        sensor_id = models.Silo.objects.filter(id=silo_id).first().sensor.id
        measures = Measurement.objects.filter(sensor=sensor_id).order_by(SAVED_DESC).all()

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
                                                                      saved__year=measure_year).order_by(SAVED_DESC)

                measures_per_day = {m.saved.strftime('%H:%M'): m.value for m in measures_per_day_objects}
                result[measure_date] = measures_per_day

        return JsonResponse(result)

    @action(methods=['get'], detail=False, url_path='graph/(?P<silo_id>[^/.]+)/(?P<timespan_type>[a-z]+)')
    def measures_for_graph(self, request, silo_id, timespan_type):
        return self._get_measures_as_json_response(KEY_FORMATS[timespan_type], silo_id, TRUNCATION[timespan_type],
                                                   DELTAS[timespan_type])

    @action(methods=['get'], detail=False,
            url_path='graph/(?P<silo_id>[^/.]+)/(?P<date_from>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z)/(?P<date_to>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z)')
    def measures_for_graph_with_time_interval(self, request, silo_id, date_from, date_to):
        date_from = parser.parse(date_from)
        date_to = parser.parse(date_to)

        if date_from > date_to:
            return JsonResponse({})
        elif date_to - date_from <= timezone.timedelta(hours=6):
            truncated_timestamp = TRUNCATION[HOUR]
            key_format = KEY_FORMATS[HOUR]
        elif date_to - date_from <= timezone.timedelta(days=1):
            truncated_timestamp = TRUNCATION[DAY]
            key_format = KEY_FORMATS[DAY]
        elif date_to - date_from <= timezone.timedelta(days=7):
            truncated_timestamp = TRUNCATION[DAY]
            key_format = "%d.%m. %H:00"
        elif date_to - date_from > timezone.timedelta(days=7):
            key_format = KEY_FORMATS[MONTH]
            truncated_timestamp = TRUNCATION[MONTH]
        else:
            return JsonResponse({})

        return self._get_measures_as_json_response(key_format, silo_id, truncated_timestamp, date_from=date_from,
                                                   date_to=date_to)

    @staticmethod
    def _get_measures_as_json_response(key_format, silo_id, truncated_timestamp,
                                       delta=None, date_from=None, date_to=None):
        if delta:
            date_to = timezone.now()
            date_from = date_to - delta

        sensor_id = models.Silo.objects.filter(id=silo_id).first().sensor.id
        base_query = Measurement.objects.filter(sensor__id=sensor_id, saved__gte=date_from, saved__lte=date_to)
        measure_dates = base_query.annotate(saved_trunc=truncated_timestamp).values('saved_trunc').annotate(
            max_date=Max(SAVED_ASC))
        max_value_dates = [m['max_date'] for m in measure_dates]

        measures = Measurement.objects.filter(sensor_id=sensor_id, saved__in=max_value_dates).order_by(SAVED_ASC)

        result = {}
        for m in measures:
            parsed_date = localtime(m.saved).strftime(key_format)
            result[parsed_date] = m.value

        return JsonResponse(result)

    @action(methods=['get'], detail=False,
            url_path='export/(?P<silo_id>[^/.]+)/(?P<date_from>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z)/(?P<date_to>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z)')
    def export_measure_for_sensor_with_time_interval(self, request, silo_id, date_from, date_to):
        date_from = parser.parse(date_from)
        date_to = parser.parse(date_to)
        return self._get_measures_as_csv(silo_id, date_from=date_from, date_to=date_to)

    @action(methods=['get'], detail=False,
            url_path='export/(?P<silo_id>[^/.]+)/(?P<timespan_type>[a-z]+)')
    def export_measure_for_sensor(self, request, silo_id, timespan_type):
        return self._get_measures_as_csv(silo_id, delta=DELTAS[timespan_type])

    @staticmethod
    def _get_measures_as_csv(silo_id, delta=None, date_from=None, date_to=None):
        if delta:
            date_to = timezone.now()
            date_from = date_to - delta

        sensor_id = models.Silo.objects.filter(id=silo_id).first().sensor.id
        time_format_in_csv = "%Y-%m-%d %H:%M:%S"
        measures = Measurement.objects.filter(sensor_id=sensor_id, saved__gte=date_from, saved__lte=date_to).order_by(
            SAVED_ASC)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="measurements.csv"'
        writer = csv.writer(response, delimiter=';')

        for measure in measures:
            writer.writerow([measure.saved.strftime(time_format_in_csv), measure.value])

        return response
