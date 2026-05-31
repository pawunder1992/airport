from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import AirplaneType, Airplane
from airport.serializers import (
    AirplaneListSerializer,
    AirplaneRetrieveSerializer,
)
from airport.tests.factories import (
    AirplaneFactory,
    AirplaneTypeFactory,
    UserFactory,
)

AIRPLANE_URL = reverse("airport:airplane-list")


def detail_url(airplane_id):
    return reverse("airport:airplane-detail", args=[airplane_id])


class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(AIRPLANE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_airplane_list(self):
        AirplaneFactory()
        AirplaneFactory()
        res = self.client.get(AIRPLANE_URL)
        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_by_airplane_type_id(self):
        plane1 = AirplaneFactory()
        plane2 = AirplaneFactory()

        res_plane1 = self.client.get(
            AIRPLANE_URL, {"airplane_type": f"{plane1.airplane_type.id}"}
        )
        res_plane2 = self.client.get(
            AIRPLANE_URL, {"airplane_type": f"{plane2.airplane_type.id}"}
        )

        serializer_plane1 = AirplaneListSerializer(plane1)
        serializer_plane2 = AirplaneListSerializer(plane2)
        self.assertEqual(len(res_plane1.data["results"]), 1)
        self.assertEqual(serializer_plane1.data, res_plane1.data["results"][0])
        self.assertEqual(serializer_plane2.data, res_plane2.data["results"][0])

    def test_retrive_airplane_details(self):
        plane = AirplaneFactory()
        url = detail_url(plane.id)
        res = self.client.get(url)
        serializer = AirplaneRetrieveSerializer(plane)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_forbidden(self):
        airplane_type = AirplaneTypeFactory()
        payload = {
            "name": "test",
            "rows": 20,
            "seats_in_row": 6,
            "airplane_type": airplane_type.id,
        }
        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_movie_not_allowed(self):
        plane = AirplaneFactory()
        url = detail_url(plane.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="test@test.test", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_create_airplane(self):
        airplane_type = AirplaneTypeFactory()
        payload = {
            "name": "test",
            "rows": 20,
            "seats_in_row": 6,
            "airplane_type": airplane_type.id,
        }
        res = self.client.post(AIRPLANE_URL, payload)
        plane = Airplane.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload.keys():
            self.assertEqual(
                payload[key],
                (
                    getattr(plane, key)
                    if key != "airplane_type"
                    else plane.airplane_type.id
                ),
            )
