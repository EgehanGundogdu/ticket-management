"invitation system tests."
from django.test import TestCase
from rest_framework.test import APIClient

# from ..serializers import StaffInvitationSerializer
from django.contrib.auth import get_user_model


class StaffInvitationTests(TestCase):
    """staff invitation tests"""

    def setUp(self):
        self.company_admin = get_user_model().objects.create_company_admin(
            first_name="Company",
            last_name="admin",
            email="test@test.com",
            password="supersecret",
        )

