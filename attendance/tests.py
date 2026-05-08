from django.test import TestCase

from core.utils import haversine_distance_meters


class GeoFenceTests(TestCase):
    def test_haversine_distance_nearby(self):
        distance = haversine_distance_meters(12.9715987, 77.5945627, 12.9716000, 77.5945600)
        self.assertLess(distance, 5)
