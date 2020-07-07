from django.test import TestCase
from rest_framework.test import APIClient
from ..serializers import StaffUserRegisterSerializer
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from ..utils import uid_token_generator


class StaffUsersRegisterTests(TestCase):
    """
    tests of registration staff users to the system.
    """

    def setUp(self):
        self.client = APIClient()
        self.registration_data = {
            "email": "test@test.com",
            "password": "testpassword",
            "password2": "testpassword",
            "first_name": "test",
            "last_name": "test",
        }

    def test_register_company_admin(self):
        """test register new company admin with valid payload"""
        payload = {
            "first_name": "Tiesto",
            "last_name": "Tiesto",
            "password": "supersecret",
            "password2": "supersecret",
            "email": "test@test.com",
        }
        res = self.client.post(reverse("accounts:register"), payload, "json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(id=res.data["id"])
        self.assertEqual(user.email, payload["email"])
        self.assertTrue(user.is_company_admin)
        self.assertFalse(user.is_active)
        self.assertTrue(user.check_password(payload["password"]))

    def test_register_company_admin_not_matched_password(self):
        """test register company admin not matched password"""
        payload = {
            "first_name": "test",
            "last_name": "test",
            "password": "supersecret",
            "password2": "notmatched",
            "email": "test@test.com",
        }
        res = self.client.post(reverse("accounts:register"), payload, "json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_company_admin_with_password_mistakes(self):
        """test register company admin with command password mistake"""
        payload = {
            "first_name": "test",
            "last_name": "test",
            "password": "123123",
            "password2": "123123",
            "email": "test@test.com",
        }
        res = self.client.post(reverse("accounts:register"), payload, "json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_succcess_message_in_response(self):
        "test success message"
        res = self.client.post(reverse("accounts:register"), self.registration_data)
        self.assertEqual(
            res.data["message"], "Check your email and activate your account."
        )

    def test_create_activate_account(self):
        """test try to user activate accouns"""
        res = self.client.post(
            reverse("accounts:register"), self.registration_data, "json"
        )
        user = get_user_model().objects.last()
        self.assertFalse(user.is_active)
        uid_and_token = uid_token_generator(user)
        res = self.client.get(reverse("accounts:activate", kwargs=uid_and_token))
        user.refresh_from_db()
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_approved, True)
