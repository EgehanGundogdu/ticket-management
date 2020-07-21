"invitation system tests."
from django.test import TestCase
from rest_framework import status
from companies.models import Company, Department
from rest_framework.test import APITestCase
from django.urls import reverse

from users.api.serializers import CompanyStaffInviteSerializer
from django.contrib.auth import get_user_model
from users.models import Invitation

OBTAIN_TOKEN_URL = reverse("accounts:token_obtain_pair")

INVITE_URL = reverse("accounts:invite")
# INVITE_CONFIRM_URL = reverse("accounts:invite-confirm")


class StaffInvitationTests(APITestCase):
    """staff invitation tests"""

    def setUp(self):
        self.company_admin = get_user_model().objects.create_company_admin(
            first_name="Company",
            last_name="admin",
            email="test@test.com",
            password="supersecret",
            is_active=True,
        )
        self.company = Company.objects.create(
            name="basic test company", leader=self.company_admin
        )
        self.department = Department.objects.create(company=self.company, name="web")
        self.access_token = self.client.post(
            OBTAIN_TOKEN_URL, {"email": "test@test.com", "password": "supersecret"}
        ).data["access"]

        self.client.force_login(self.company_admin)

    def test_invite_employee(self):
        payload = {
            "first_name": "invited1",
            "last_name": "invited1",
            "email": "invited@test.com",
            "is_staff": True,
            "company": self.company.id,
        }

        res = self.client.post(INVITE_URL, payload, "json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Invitation.objects.first().first_name, payload["first_name"])

    def test_invite_multiple_employee(self):
        payload = [
            {
                "first_name": "invited1",
                "last_name": "invited1",
                "email": "invited@test.com",
                "is_staff": False,
                "company": self.company.id,
            },
            {
                "first_name": "invited2",
                "last_name": "invited2",
                "email": "invited2@test.com",
                "is_staff": False,
                "company": self.company.id,
            },
        ]
        self.client.force_login(self.company_admin)
        res = self.client.post(INVITE_URL, payload, "json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Invitation.objects.count(), 2)

    def test_invite_staff(self):
        payload = {
            "first_name": "invited1",
            "last_name": "invited1",
            "email": "invited@test.com",
            "is_staff": True,
            "company": self.company.id,
            "department": self.department.id,
        }
        self.client.force_login(self.company_admin)
        res = self.client.post(INVITE_URL, payload, "json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Invitation.objects.first().first_name, payload["first_name"])

    def test_invite_multiple_staff(self):
        payload = [
            {
                "first_name": "invited1",
                "last_name": "invited1",
                "email": "invited@test.com",
                "is_staff": True,
                "company": self.company.id,
                "department": self.department.id,
            },
            {
                "first_name": "invited2",
                "last_name": "invited2",
                "email": "invited2@test.com",
                "is_staff": True,
                "company": self.company.id,
                "department": self.department.id,
            },
        ]

        self.client.force_login(self.company_admin)
        res = self.client.post(INVITE_URL, payload, "json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_staff__invite_and_confirm(self):
        invite_payload = {
            "first_name": "invited",
            "last_name": "confirmed",
            "email": "swing@hey.com",
            "company": self.company.id,
            "department": self.department.id,
            "is_staff": True,
        }
        serializer = CompanyStaffInviteSerializer(data=invite_payload)
        if serializer.is_valid():
            serializer.save(inviter=self.company_admin)
        invite = Invitation.objects.get(id=serializer.data["id"])
        res = self.client.get(
            reverse("accounts:invite-confirm", kwargs={"uuid": invite.uuid})
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user = get_user_model().objects.get(email=invite.email)
        self.assertIn(user.id, self.company.employees.values_list("id", flat=True))
        self.assertIn(user.id, self.department.members.values_list("id", flat=True))
        invite.refresh_from_db()
        self.assertTrue(invite.confirmed)

    def test_invite_customer(self):
        invite_payload = {
            "first_name": "invited",
            "last_name": "customer",
            "email": "customer@test.com",
            "is_staff": False,
            "company": self.company.id,
        }
        serializer = CompanyStaffInviteSerializer(data=invite_payload)
        if serializer.is_valid():
            serializer.save(inviter=self.company_admin)
        invite = Invitation.objects.get(id=serializer.data["id"])
        res = self.client.get(
            reverse("accounts:invite-confirm", kwargs={"uuid": invite.uuid})
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user = get_user_model().objects.get(email=invite.email)
        self.assertIn(user.id, self.company.customers.values_list("id", flat=True))
        invite.refresh_from_db()
        self.assertTrue(invite.confirmed)
