# Create your views here.
from rest_framework import viewsets

from api import models, serializers


class SiloViewSet(viewsets.ModelViewSet):
    queryset = models.Silo.objects.all()
    serializer_class = serializers.SiloSerializer


class LaserViewSet(viewsets.ModelViewSet):
    queryset = models.Laser.objects.all()
    serializer_class = serializers.LaserSerializer


class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = models.Measurement.objects.all()
    serializer_class = serializers.MeasurementSerializer
