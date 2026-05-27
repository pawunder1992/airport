from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from airport.serializers import RouteListSerializer
from airport.tests.factories import AirportFactory, RouteFactory

ROUTE_URL = reverse("airport:route-list")


def detail_url(route_id):
    return reverse("airport:route-detail", args=[route_id])



class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class AdminRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="test@test.test", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_create_route_with_same_source_and_destination_fails(self):
        source = AirportFactory()
        payload = {
            "source": source.id,
            "destination": source.id,
            "distance": 1000,
        }
        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("destination can`t be same as source", str(res.data))

    def test_filter_routes_by_source_or_destination(self):
        kyiv_airport = AirportFactory(city="Kyiv")
        london_airport = AirportFactory(city="London")
        paris_airport = AirportFactory(city="Paris")
        route1 = RouteFactory(source=kyiv_airport, destination=paris_airport)
        route2 = RouteFactory(source=paris_airport, destination=london_airport)
        res_source = self.client.get(ROUTE_URL, {"source_city": f"{kyiv_airport.city}"})
        res_destination = self.client.get(ROUTE_URL, {"destination_city": f"{london_airport.city}"})
        self.assertEqual(res_source.status_code, status.HTTP_200_OK)
        self.assertEqual(res_destination.status_code, status.HTTP_200_OK)
        serializer_route1 = RouteListSerializer(route1)
        serializer_route2 = RouteListSerializer(route2)
        self.assertEqual(len(res_source.data["results"]), 1)
        self.assertEqual(len(res_destination.data["results"]), 1)
        self.assertEqual(serializer_route1.data, res_source.data["results"][0])
        self.assertEqual(serializer_route2.data, res_destination.data["results"][0])



