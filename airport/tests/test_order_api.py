from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from airport.serializers import OrderListSerializer
from airport.tests.factories import UserFactory, OrderFactory, AirplaneFactory, \
    FlightFactory

ORDER_URL = reverse("airport:order-list")



class UnauthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_visible_only_user_orders(self):
        user_ivan = UserFactory(email="ivan@test.com")
        user_order = OrderFactory(user=self.user)
        OrderFactory(user=user_ivan)
        response = self.client.get(ORDER_URL)
        serializer = OrderListSerializer(user_order)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0], serializer.data)

    def test_create_ticket_with_invalid_rows(self):
        airplane = AirplaneFactory(rows=10, seats_in_row=6)
        flight = FlightFactory(airplane=airplane)
        payload = {
            "tickets": [
                {
                    "flight": flight.id,
                    "row": 11,
                    "seat": "A",
                }
            ]
        }
        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("row", str(res.data))

    def test_create_ticket_with_invalid_seat(self):
        airplane = AirplaneFactory(rows=10, seats_in_row=6)
        flight = FlightFactory(airplane=airplane)
        payload = {
            "tickets": [
                {
                    "flight": flight.id,
                    "row": 9,
                    "seat": "Z",
                }
            ]
        }
        res = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("seat", str(res.data))



