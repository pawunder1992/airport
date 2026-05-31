from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient
from rest_framework import status

from airport.serializers import RouteListSerializer
from airport.tests.factories import (
    AirportFactory,
    RouteFactory,
    FlightFactory,
    AirplaneFactory,
    CrewFactory,
    TicketFactory,
)

FLIGHT_URL = reverse("airport:flight-list")


def detail_url(flight_id):
    return reverse("airport:flight-detail", args=[flight_id])


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminFlightApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="test@test.test", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_flight_departure_time_cannot_be_after_arrival_time(self):
        route = RouteFactory()
        airplane = AirplaneFactory()
        crew = CrewFactory()
        departure = timezone.now() + timedelta(hours=2)
        arrival = timezone.now() - timedelta(hours=5)

        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": departure.isoformat(),
            "arrival_time": arrival.isoformat(),
            "crew": [crew.id],
        }
        res = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "departure_time can`t be greater than arrival_time", str(res.data)
        )

    def test_flight_time_less_than_current_time(self):
        route = RouteFactory()
        airplane = AirplaneFactory()
        crew = CrewFactory()
        departure = timezone.now() - timedelta(hours=2)
        arrival = timezone.now() + timedelta(hours=5)

        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": departure.isoformat(),
            "arrival_time": arrival.isoformat(),
            "crew": [crew.id],
        }
        res = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "Departure time can't be less than current time (in the past).",
            str(res.data),
        )

    def test_flight_available_seats_decreases(self):
        airplane = AirplaneFactory(rows=10, seats_in_row=6)
        flight = FlightFactory(airplane=airplane)
        TicketFactory(flight=flight, row=1, seat="A")
        TicketFactory(flight=flight, row=1, seat="B")
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"][0]["tickets_available"], 58)

    def test_filter_flights_by_date(self):
        tomorrow = timezone.now() + timedelta(days=1)
        next_week = timezone.now() + timedelta(days=7)
        flight_tomorrow = FlightFactory(
            departure_time=tomorrow, arrival_time=next_week
        )
        filter_date_str = tomorrow.date().isoformat()
        res = self.client.get(FLIGHT_URL, {"date": filter_date_str})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["id"], flight_tomorrow.id)

    def test_filter_flights_by_source_city_icontains(self):
        kyiv_airport = AirportFactory(city="Kyiv")
        paris_airport = AirportFactory(city="Paris")
        route_from_kyiv = RouteFactory(source=kyiv_airport)
        route_from_paris = RouteFactory(source=paris_airport)
        flight_kyiv = FlightFactory(route=route_from_kyiv)
        FlightFactory(route=route_from_paris)
        res = self.client.get(FLIGHT_URL, {"source_city": "kyiv"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["id"], flight_kyiv.id)
