# Create your views here.
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from api import models, serializers


class SiloViewSet(viewsets.ModelViewSet):
    queryset = models.Silo.objects.all()
    serializer_class = serializers.SiloSerializer


class SensorViewSet(viewsets.ModelViewSet):
    queryset = models.Sensor.objects.all()
    serializer_class = serializers.SensorSerializer


class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = models.Measurement.objects.all()
    serializer_class = serializers.MeasurementSerializer
