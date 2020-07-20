# from django.test import TestCase
# from rest_framework.test import APIClient
# from rest_framework import status
# from rest_framework.authtoken.models import Token
# from django.contrib.auth import get_user_model
# from django.urls import reverse


# OBTAIN_TOKEN_URL = reverse("accounts:obtain-token")


# class AuthenticationTest(TestCase):
#     """user authentication tests"""

#     def setUp(self):
#         self.client = APIClient()
#         self.inactive_user = get_user_model().objects.create_inactive_user(
#             email="inactive@test.com", password="testpass"
#         )
#         self.active_user = get_user_model().objects.create_user(
#             email="active@test.com", password="testpass", is_active=True
#         )

#     def test_method_not_allowed(self):
#         """test obtain token endpoint not supported get method"""
#         res = self.client.get(OBTAIN_TOKEN_URL)
#         self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

#     def test_not_allowed_inactive_user(self):
#         """test obtain token endpoint with not active user."""
#         payload = {"email": "inactive@test.com", "password": "testpass"}
#         res = self.client.post(OBTAIN_TOKEN_URL, payload, "json")
#         self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertContains(
#             res,
#             "Unable to log in with provided credentials.",
#             status_code=status.HTTP_400_BAD_REQUEST,
#         )

#     def test_obtain_token_with_active_user(self):
#         """test obtain token succesfully with active user."""
#         payload = {"email": "active@test.com", "password": "testpass"}
#         res = self.client.post(OBTAIN_TOKEN_URL, payload, "json")
#         token = Token.objects.get(user=self.active_user)
#         self.assertEqual(res.data["token"], token.key)
