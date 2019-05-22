from datetime import datetime, timedelta
from unittest import mock

import pytz
from django.test import TestCase

from api.models import Silo, Sensor, Measurement


class SiloTest(TestCase):

    def test_average_values(self):
        sensor = Sensor.objects.create(serial_number='222')

        # this is needed to bypass `auto_now_add` in `saved` field
        with mock.patch('django.utils.timezone.now') as mock_now:
            testing_date = datetime(2019, 5, 20, 9, tzinfo=pytz.UTC)
            mock_now.return_value = testing_date

            Measurement.objects.create(sensor=sensor, value=1, saved=testing_date)
            testing_date = testing_date - timedelta(days=1)
            mock_now.return_value = testing_date
            Measurement.objects.create(sensor=sensor, value=2, saved=testing_date)
            Measurement.objects.create(sensor=sensor, value=4, saved=testing_date)

            testing_date = testing_date - timedelta(days=1)
            mock_now.return_value = testing_date
            Measurement.objects.create(sensor=sensor, value=5, saved=testing_date)
            testing_date = testing_date - timedelta(days=1)
            mock_now.return_value = testing_date
            Measurement.objects.create(sensor=sensor, value=6, saved=testing_date)

        silo = Silo.objects.create(name="test_silo", sensor=sensor)

        result = silo.last_days_in_average()

        self.assertEqual(3, len(result))
        self.assertEquals(result['2019-05-20'], 1)  # one measure for this day
        self.assertEquals(result['2019-05-19'], 3)  # two measures, average is 3
        self.assertEquals(result['2019-05-18'], 5)  # one measure for this day
        self.assertEquals(result.pop('2019-05-17', 'no value found'),
                          'no value found')  # no measure should be for this date

    def test_average_values2(self):
        sensor = Sensor.objects.create(serial_number='222')

        # this is needed to bypass `auto_now_add` in `saved` field
        with mock.patch('django.utils.timezone.now') as mock_now:
            testing_date = datetime(2019, 3, 23, 18, 41, tzinfo=pytz.UTC)
            mock_now.return_value = testing_date
            Measurement.objects.create(sensor=sensor, value=20, saved=testing_date)

            testing_date = datetime(2019, 3, 23, 17, 41, tzinfo=pytz.UTC)
            mock_now.return_value = testing_date
            Measurement.objects.create(sensor=sensor, value=24, saved=testing_date)
            # Measurement.objects.create(sensor=sensor, value=4, saved=testing_date)

            testing_date = datetime(2019, 3, 22, 17, 41, tzinfo=pytz.UTC)
            mock_now.return_value = testing_date
            Measurement.objects.create(sensor=sensor, value=37, saved=testing_date)

            testing_date = datetime(2019, 3, 21, 17, 41, tzinfo=pytz.UTC)
            mock_now.return_value = testing_date
            Measurement.objects.create(sensor=sensor, value=41, saved=testing_date)

        silo = Silo.objects.create(name="test_silo", sensor=sensor)

        result = silo.last_days_in_average()

        self.assertEqual(3, len(result))
        self.assertEquals(result['2019-03-23'], 22)  # one measure for this day
        self.assertEquals(result['2019-03-22'], 37)  # two measures, average is 3
        self.assertEquals(result['2019-03-21'], 41)  # one measure for this day
