from rest_framework.test import APITestCase
from django.test import TestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from companies.models import Company, Department
from ..models import Ticket
from tickets.api.serializers import CompanyAdminTicketSerializer


def generate_ticket_test_url(ticket=None):
    """populate ticket url helper function."""
    if ticket is None:
        return reverse("tickets:ticket-list")
    return reverse("tickets:ticket-detail", kwargs={"identifier": ticket.identifier})


def generate_dummy_ticket(**kwargs):

    return Ticket.objects.create(**kwargs)


class PublicTicketAPITests(APITestCase):
    """tests for public ticket api endpoints."""

    def test_get_tickets_unauthenticated_user(self):
        """test get company ticket with unauthenticated user"""
        url = generate_ticket_test_url()
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTicketAPITests(APITestCase):
    def setUp(self):
        self.company_1_customer = get_user_model().objects.create_user(
            email="customer@company1.com", password="supersecret", is_active=True
        )
        self.company_2_customer = get_user_model().objects.create_user(
            email="customer@company2.com", password="supersecret", is_active=True
        )
        self.company_1_staff = get_user_model().objects.create_staff_user(
            email="staff@company1.com", password="supersecret", is_active=True
        )
        self.company_2_staff = get_user_model().objects.create_staff_user(
            email="staff2@company2.com", password="supersecret", is_active=True
        )
        self.company_1_admin = get_user_model().objects.create_company_admin(
            email="admin@company1.com", password="supersecret", is_active=True
        )
        self.company_2_admin = get_user_model().objects.create_company_admin(
            email="admin@company2.com", password="supersecret", is_active=True
        )
        self.company_1 = Company.objects.create(
            leader=self.company_1_admin, name="Company1"
        )
        self.company_2 = Company.objects.create(
            leader=self.company_2_admin, name="Company2"
        )
        self.company_1_department = Department.objects.create(
            company=self.company_1, name="Web"
        )

        self.company_2_department = Department.objects.create(
            company=self.company_2, name="System"
        )
        self.company_1.employees.add(self.company_1_staff)
        self.company_1.customers.add(self.company_1_customer)
        self.company_1_department.members.add(self.company_1_staff)

        self.ticket = Ticket.objects.create(
            header="test ticket",
            content="test ticket content",
            company=self.company_1,
            department=self.company_1_department,
            owner=self.company_1_customer,
        )

        # company2 initialization
        self.company_2.employees.add(self.company_2_staff)
        self.company_2.customers.add(self.company_2_customer)
        self.company_2_department.members.add(self.company_2_staff)

    def test_create_new_ticket_as_a_customer(self):
        """A new ticket creation test as a company customer."""
        payload = {
            "header": "Test ticket",
            "content": "Test ticket content",
            "company": self.company_1.id,
            "department": self.company_1_department.id,
        }
        self.client.force_authenticate(self.company_1_customer)
        url = generate_ticket_test_url()
        res = self.client.post(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_a_ticket_as_a_owner(self):
        """a ticket update test as a ticket owner."""
        payload = {"content": "updated ticket content!"}
        url = generate_ticket_test_url(self.ticket)
        self.client.force_authenticate(self.company_1_customer)
        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(res.data["content"], payload["content"])

    def test_get_a_ticket_not_owner_or_company_leader(self):
        """a ticket get test as not_owner_or_company_leader."""
        self.client.force_authenticate(self.company_2_customer)
        url = generate_ticket_test_url(self.ticket)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_ticket_as_a_company_leader(self):
        url = generate_ticket_test_url()
        ticket1 = {
            "header": "dummy",
            "content": "dummy",
            "owner": self.company_1_customer,
            "department": self.company_1_department,
            "company": self.company_1,
        }
        ticket2 = {
            "header": "dummy",
            "content": "dummy",
            "owner": self.company_1_customer,
            "department": self.company_1_department,
            "company": self.company_1,
        }
        ticket3 = {
            "header": "dummy",
            "content": "dummy",
            "owner": self.company_2_customer,
            "department": self.company_2_department,
            "company": self.company_2,
        }

        generate_dummy_ticket(**ticket1)
        generate_dummy_ticket(**ticket2)
        generate_dummy_ticket(**ticket3)
        self.client.force_authenticate(self.company_2_admin)
        url = generate_ticket_test_url()
        res = self.client.get(url)

        serializer = CompanyAdminTicketSerializer(
            Ticket.objects.filter(company__leader=self.company_2_admin), many=True
        )
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(serializer.data), 1)

    def test_update_ticket_as_a_company_leader(self):
        url = generate_ticket_test_url(self.ticket)
        payload = {
            "priorty": 3,
            "content": "admin updated this content",
            "related_user": self.company_1_staff.id,
        }
        self.client.force_authenticate(self.company_1_admin)

        res = self.client.patch(url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.content, payload["content"])

        self.assertEqual(self.ticket.related_user, self.company_1_staff)

    def test_update_ticket_as_a_company_staff(self):
        payload = {"content": "not updated "}
        self.client.force_authenticate(self.company_1_staff)
        url = generate_ticket_test_url(self.ticket)
        res = self.client.patch(url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_tickets_as_a_department_staff(self):
        url = generate_ticket_test_url()
        company_2_department_2 = Department.objects.create(
            company=self.company_2, name="mobile"
        )

        ticket2 = {
            "header": "dummy",
            "content": "dummy",
            "owner": self.company_2_customer,
            "department": self.company_2_department,
            "company": self.company_2,
        }
        ticket3 = {
            "header": "dummy",
            "content": "dummy",
            "owner": self.company_2_customer,
            "department": company_2_department_2,
            "company": self.company_2,
        }

        generate_dummy_ticket(**ticket2)
        generate_dummy_ticket(**ticket3)
        self.client.force_authenticate(self.company_2_staff)
        url = generate_ticket_test_url()
        res = self.client.get(url)

        serializer = CompanyAdminTicketSerializer(
            Ticket.objects.filter(department__members__id=self.company_2_staff.id),
            many=True,
        )
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(serializer.data), 1)
