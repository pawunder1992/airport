import os
import shutil
import tempfile
from PIL import Image

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse

from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from airport.models import Airplane
from airport.tests.factories import AirplaneFactory, AirplaneTypeFactory

AIRPLANE_URL = reverse("airport:airplane-list")


def image_upload_url(airplane_id):
    return reverse("airport:airplane-upload-image", args=[airplane_id])


def detail_url(airplane_id):
    return reverse("airport:airplane-detail", args=[airplane_id])


TEST_DIR = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_DIR)
class AirplaneImageUploadTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.airplane = AirplaneFactory()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        shutil.rmtree(TEST_DIR, ignore_errors=True)

    def test_upload_image_to_airplane(self):

        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")

        self.airplane.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airplane.image.path))

    def test_upload_image_bad_request(self):

        url = image_upload_url(self.airplane.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_airplane_list(self):
        url = AIRPLANE_URL
        airplane_type = AirplaneTypeFactory()

        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "name": "Plane",
                    "rows": 10,
                    "seats_in_row": 10,
                    "airplane_type": airplane_type.id,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane = Airplane.objects.get(name="Plane")
        self.assertFalse(airplane.image)

    def test_image_url_is_shown_on_airplane_detail(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")

        res = self.client.get(detail_url(self.airplane.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_airplane_list(self):
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")

        res = self.client.get(AIRPLANE_URL)

        if "results" in res.data:
            airplane_data = res.data["results"][0]
        else:
            airplane_data = res.data[0]

        self.assertIn("image", airplane_data.keys())
