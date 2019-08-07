from datetime import datetime
from unittest import mock

import pytz
from django.test import TestCase
from freezegun import freeze_time

from api.models import Silo, Sensor, Measurement
from api.views import _measures_by_hour, _measures_by_day, _measures_by_week, _measures_by_month


class SiloTest(TestCase):

    def test_values_by_day(self):
        sensor = Sensor.objects.create(serial_number='222')

        values = {
            datetime(2019, 5, 20, 9, tzinfo=pytz.UTC): 1,
            datetime(2019, 5, 19, 9, 0, tzinfo=pytz.UTC): 2,
            datetime(2019, 5, 19, 9, 1, tzinfo=pytz.UTC): 4,
            datetime(2019, 5, 18, 9, tzinfo=pytz.UTC): 5,
            datetime(2019, 5, 17, 9, tzinfo=pytz.UTC): 6,

        }

        self.create_test_measurements(sensor, values)

        silo = Silo.objects.create(name="test_silo", sensor=sensor)

        result = silo.values_by_day()

        self.assertEqual(3, len(result))
        self.assertEquals(result['2019-05-19'], 4)
        self.assertEquals(result['2019-05-18'], 5)
        self.assertEquals(result['2019-05-17'], 6)
        self.assertEquals(result.pop('2019-05-20', 'skipped'),
                          'skipped')

    def test_values_by_day2(self):
        sensor = Sensor.objects.create(serial_number='222')

        values = {
            datetime(2019, 3, 23, 18, 41, tzinfo=pytz.UTC): 20,
            datetime(2019, 3, 22, 18, 41, tzinfo=pytz.UTC): 24,
            datetime(2019, 3, 22, 17, 41, tzinfo=pytz.UTC): 37,
            datetime(2019, 3, 21, 17, 41, tzinfo=pytz.UTC): 41,

        }

        self.create_test_measurements(sensor, values)

        silo = Silo.objects.create(name="test_silo", sensor=sensor)

        result = silo.values_by_day()

        self.assertEqual(2, len(result))
        self.assertEquals(result['2019-03-22'], 24)
        self.assertEquals(result['2019-03-21'], 41)
        self.assertEquals(result.pop('2019-05-23', 'skipped'),
                          'skipped')

    @freeze_time("2019-03-23 18:45")
    def test_measures_by_hour(self):
        sensor_id = 1
        sensor = Sensor.objects.create(serial_number='222', id=sensor_id)
        values = {
            datetime(2019, 3, 23, 18, 43, 30, tzinfo=pytz.UTC): 64,
            datetime(2019, 3, 23, 18, 42, 31, tzinfo=pytz.UTC): 62,
            datetime(2019, 3, 23, 18, 42, 30, tzinfo=pytz.UTC): 60,
            datetime(2019, 3, 23, 18, 41, 30, tzinfo=pytz.UTC): 58,
            datetime(2019, 3, 23, 18, 40, 32, tzinfo=pytz.UTC): 56,
            datetime(2019, 3, 23, 18, 40, 31, tzinfo=pytz.UTC): 54,
            datetime(2019, 3, 23, 18, 40, 30, tzinfo=pytz.UTC): 52,
            datetime(2019, 3, 23, 18, 39, 30, tzinfo=pytz.UTC): 50,
            datetime(2019, 3, 23, 15, 39, 30, tzinfo=pytz.UTC): 50,
            datetime(2019, 3, 21, 15, 39, 30, tzinfo=pytz.UTC): 50,
            # and one in the future
            datetime(2020, 3, 21, 15, 39, 30, tzinfo=pytz.UTC): 50,

        }

        self.create_test_measurements(sensor, values)

        response = _measures_by_hour(sensor_id)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"18:39": 50.0, "18:40": 56.0, "18:41": 58.0, "18:42": 62.0, "18:43": 64.0}
        )

    @freeze_time("2019-03-23 18:45")
    def test_measures_by_day(self):
        sensor_id = 1
        sensor = Sensor.objects.create(serial_number='222', id=sensor_id)

        values = {
            datetime(2019, 3, 23, 14, 43, 30, tzinfo=pytz.UTC): 64,
            datetime(2019, 3, 23, 14, 42, 31, tzinfo=pytz.UTC): 62,
            datetime(2019, 3, 23, 13, 42, 30, tzinfo=pytz.UTC): 60,
            datetime(2019, 3, 23, 13, 41, 30, tzinfo=pytz.UTC): 58,
            datetime(2019, 3, 23, 13, 40, 32, tzinfo=pytz.UTC): 56,
            datetime(2019, 3, 23, 12, 45, 31, tzinfo=pytz.UTC): 54,
            datetime(2019, 3, 23, 12, 40, 30, tzinfo=pytz.UTC): 52,
            datetime(2019, 3, 23, 11, 39, 30, tzinfo=pytz.UTC): 50,
            datetime(2019, 3, 22, 11, 39, 30, tzinfo=pytz.UTC): 50,
        }

        self.create_test_measurements(sensor, values)

        response = _measures_by_day(sensor_id)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"11:00": 50.0, "12:00": 54.0, "13:00": 60.0, "14:00": 64.0}
        )

    @freeze_time("2019-03-23 18:45")
    def test_measures_by_week(self):
        sensor_id = 1
        sensor = Sensor.objects.create(serial_number='222', id=sensor_id)

        values = {
            datetime(2019, 3, 23, 14, 48, 30, tzinfo=pytz.UTC): 68,
            datetime(2019, 3, 23, 11, 46, 30, tzinfo=pytz.UTC): 67,
            datetime(2019, 3, 22, 16, 44, 31, tzinfo=pytz.UTC): 66,
            datetime(2019, 3, 22, 14, 42, 31, tzinfo=pytz.UTC): 65,
            datetime(2019, 3, 21, 14, 46, 30, tzinfo=pytz.UTC): 64,
            datetime(2019, 3, 21, 13, 42, 30, tzinfo=pytz.UTC): 63,
            datetime(2019, 3, 20, 15, 46, 30, tzinfo=pytz.UTC): 62,
            datetime(2019, 3, 20, 14, 44, 30, tzinfo=pytz.UTC): 61,
            datetime(2019, 3, 20, 13, 41, 30, tzinfo=pytz.UTC): 60,
            datetime(2019, 3, 19, 14, 42, 32, tzinfo=pytz.UTC): 59,
            datetime(2019, 3, 19, 13, 40, 32, tzinfo=pytz.UTC): 58,
            datetime(2019, 3, 18, 13, 47, 31, tzinfo=pytz.UTC): 57,
            datetime(2019, 3, 18, 12, 45, 31, tzinfo=pytz.UTC): 56,
            datetime(2019, 3, 17, 15, 42, 30, tzinfo=pytz.UTC): 55,
            datetime(2019, 3, 17, 14, 41, 30, tzinfo=pytz.UTC): 54,
            datetime(2019, 3, 17, 12, 40, 30, tzinfo=pytz.UTC): 53,
            datetime(2019, 3, 16, 14, 39, 30, tzinfo=pytz.UTC): 52,
            datetime(2019, 3, 16, 13, 39, 30, tzinfo=pytz.UTC): 51,
            datetime(2019, 3, 16, 11, 39, 30, tzinfo=pytz.UTC): 50,
            datetime(2019, 3, 15, 11, 39, 30, tzinfo=pytz.UTC): 50,
        }

        self.create_test_measurements(sensor, values)

        response = _measures_by_week(sensor_id)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"23.03": 68.0, "22.03": 66.0, "21.03": 64.0, "20.03": 62.0, "19.03": 59.0, "18.03": 57.0, "17.03": 55.0}
        )

    @freeze_time("2019-03-23 18:45")
    def test_measures_by_month(self):
        sensor_id = 1
        sensor = Sensor.objects.create(serial_number='222', id=sensor_id)

        values = {
            datetime(2019, 3, 23, 14, 48, 30, tzinfo=pytz.UTC): 68,
            datetime(2019, 3, 23, 11, 46, 30, tzinfo=pytz.UTC): 67,
            datetime(2019, 3, 15, 15, 44, 31, tzinfo=pytz.UTC): 66,
            datetime(2019, 3, 15, 14, 42, 31, tzinfo=pytz.UTC): 65,
            datetime(2019, 3, 13, 15, 46, 30, tzinfo=pytz.UTC): 64,
            datetime(2019, 3, 13, 13, 42, 30, tzinfo=pytz.UTC): 63,
            datetime(2019, 3, 10, 15, 46, 30, tzinfo=pytz.UTC): 62,
            datetime(2019, 3, 10, 14, 44, 30, tzinfo=pytz.UTC): 61,
            datetime(2019, 3, 10, 13, 41, 30, tzinfo=pytz.UTC): 60,
            datetime(2019, 3, 9, 14, 42, 32, tzinfo=pytz.UTC): 59,
            datetime(2019, 3, 9, 13, 40, 32, tzinfo=pytz.UTC): 58,
            datetime(2019, 3, 8, 14, 47, 31, tzinfo=pytz.UTC): 57,
            datetime(2019, 3, 8, 12, 45, 31, tzinfo=pytz.UTC): 56,
            datetime(2019, 3, 7, 14, 42, 30, tzinfo=pytz.UTC): 55,
            datetime(2019, 3, 7, 13, 41, 30, tzinfo=pytz.UTC): 54,
            datetime(2019, 3, 7, 12, 40, 30, tzinfo=pytz.UTC): 53,
            datetime(2019, 3, 6, 13, 39, 30, tzinfo=pytz.UTC): 52,
            datetime(2019, 3, 6, 12, 39, 30, tzinfo=pytz.UTC): 51,
            datetime(2019, 3, 6, 11, 39, 30, tzinfo=pytz.UTC): 50,
            datetime(2019, 3, 5, 11, 39, 30, tzinfo=pytz.UTC): 50,
        }

        self.create_test_measurements(sensor, values)

        response = _measures_by_month(sensor_id)

        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"23.03": 68.0, "15.03": 66.0, "13.03": 64.0, "10.03": 62.0, "09.03": 59.0, "08.03": 57.0, "07.03": 55.0,
             "06.03": 52.0, "05.03": 50.0}
        )

    @staticmethod
    def create_test_measurements(sensor, values):
        # this is needed to bypass `auto_now_add` in `saved` field
        with mock.patch('django.utils.timezone.now') as mock_now:
            for key, value in values.items():
                mock_now.return_value = key
                Measurement.objects.create(sensor=sensor, value=value)
