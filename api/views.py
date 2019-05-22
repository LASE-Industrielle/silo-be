# Create your views here.
from django.http import JsonResponse
from rest_framework import viewsets

from api import models, serializers
from api.models import Measurement


class SiloViewSet(viewsets.ModelViewSet):
    queryset = models.Silo.objects.all()
    serializer_class = serializers.SiloSerializer


class SensorViewSet(viewsets.ModelViewSet):
    queryset = models.Sensor.objects.all()
    serializer_class = serializers.SensorSerializer


class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = models.Measurement.objects.all()
    serializer_class = serializers.MeasurementSerializer


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
