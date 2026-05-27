from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from airport.models import AirplaneType, Airplane
from airport.serializers import AirplaneListSerializer, AirplaneRetrieveSerializer
from airport.tests.factories import AirplaneFactory, AirplaneTypeFactory, UserFactory

AIRPLANE_URL = reverse("airport:airplane-list")


def detail_url(airplane_id):
    return reverse("airport:airplane-detail", args=[airplane_id])

class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()