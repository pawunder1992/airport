from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

CREATE_USER_URL = reverse("user:create")
MANAGE_USER_URL = reverse("user:manage_user")


class UserManagerTests(TestCase):

    def test_create_user_successful(self):

        email = "test@example.com"
        password = "SecurePassword123"
        user = get_user_model().objects.create_user(
            email=email, password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(
            hasattr(user, "username") and user.username is not None
        )

    def test_create_superuser_successful(self):
        email = "admin@example.com"
        password = "AdminPassword123"
        user = get_user_model().objects.create_superuser(
            email=email, password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_user_raises_value_error_if_no_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email="", password="password123"
            )

    def test_email_normalization(self):
        email = "user@EXAMPLE.COM"
        user = get_user_model().objects.create_user(
            email=email, password="password123"
        )
        self.assertEqual(user.email, "user@example.com")


class PublicUserApiTests(APITestCase):

    def test_create_user_api_success(self):
        payload = {
            "email": "newuser@example.com",
            "password": "validpassword123",
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(response.data["email"], payload["email"])
        self.assertNotIn("password", response.data)

    def test_create_user_duplicate_email_fails(self):
        email = "duplicate@example.com"
        get_user_model().objects.create_user(
            email=email, password="password123"
        )

        payload = {"email": email, "password": "newpassword123"}
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_override_read_only_fields(self):
        payload = {
            "email": "hacker@example.com",
            "password": "password123",
            "is_staff": True,
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(id=response.data["id"])
        self.assertFalse(user.is_staff)

    def test_create_user_with_empty_fields_fails(self):
        payload = {"email": "", "password": ""}
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateUserApiTests(APITestCase):

    def setUp(self):
        self.password = "initialpassword123"
        self.user = get_user_model().objects.create_user(
            email="profileowner@example.com", password=self.password
        )
        self.client.force_authenticate(user=self.user)

    def test_anonymous_access_denied(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(MANAGE_USER_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_own_profile_success(self):
        response = self.client.get(MANAGE_USER_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertNotIn("password", response.data)

    def test_update_email_success(self):
        payload = {"email": "newemail@example.com"}
        response = self.client.patch(MANAGE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, payload["email"])

    def test_update_password_hashes_correctly(self):
        new_password = "brandnewpassword123"
        payload = {"password": new_password}
        response = self.client.patch(MANAGE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(self.password))
        self.assertTrue(self.user.check_password(new_password))

    def test_update_profile_without_password_keeps_old_password(self):
        payload = {"email": "anotheremail@example.com"}
        response = self.client.patch(MANAGE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()

        self.assertEqual(self.user.email, payload["email"])

        self.assertTrue(self.user.check_password(self.password))
