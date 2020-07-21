# from rest_framework.test import APIClient
# from django.test import TestCase
# from rest_framework import status
# from django.urls import reverse
# from django.contrib.auth import get_user_model
# from companies.models import Company, Department
# from ..models import Ticket


# def generate_ticket_test_url(ticket=None):
#     """populate ticket url helper function."""
#     if ticket is None:
#         return reverse("tickets:ticket-list")
#     return reverse("tickets:ticket-detail", kwargs={"identifier": ticket.identifier})


# class PublicTicketAPITests(TestCase):
#     """tests for public ticket api endpoints."""

#     def setUp(self):
#         self.client = APIClient()

#     def test_get_tickets_unauthenticated_user(self):
#         """test get company ticket with unauthenticated user"""
#         url = generate_ticket_test_url()
#         res = self.client.get(url)
#         self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# class PrivateTicketAPITests(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.normal_user = get_user_model().objects.create_user(
#             email="normal@test.com", password="supersecret", is_active=True
#         )
#         self.normal_user2 = get_user_model().objects.create_user(
#             email="normal2@test.com", password="supersecret", is_active=True
#         )
#         self.staff_user = get_user_model().objects.create_staff_user(
#             email="staff@test.com", password="supersecret", is_active=True
#         )
#         self.staff_user2 = get_user_model().objects.create_staff_user(
#             email="staff2@test.com", password="supersecret", is_active=True
#         )
#         self.company_admin = get_user_model().objects.create_company_admin(
#             email="company@admin.com", password="supersecret", is_active=True
#         )
#         self.company = Company.objects.create(
#             leader=self.company_admin, name="Test Mobile"
#         )
#         self.department = Department.objects.create(company=self.company, name="Web")
#         self.company.employees.add(self.staff_user, self.staff_user2)
#         self.company.customers.add(self.normal_user)
#         self.department.members.add(self.staff_user)
#         self.ticket = Ticket.objects.create(
#             header="test ticket",
#             content="test ticket content",
#             company=self.company,
#             department=self.department,
#             owner=self.normal_user,
#         )

#     def test_create_new_ticket_as_a_customer(self):
#         """A new ticket creation test as a company customer."""
#         payload = {
#             "header": "Test ticket",
#             "content": "Test ticket content",
#             "company": self.company.id,
#             "department": self.department.id,
#         }
#         self.client.force_authenticate(self.normal_user)
#         url = generate_ticket_test_url()
#         res = self.client.post(url, payload, "json")
#         print(res.data)
#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)

#     def test_update_a_ticket_as_a_owner(self):
#         """a ticket update test as a ticket owner."""
#         payload = {"content": "updated ticket content!"}
#         url = generate_ticket_test_url(self.ticket)
#         self.client.force_authenticate(self.normal_user)
#         res = self.client.patch(url, payload, "json")
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.ticket.refresh_from_db()
#         self.assertEqual(res.data["content"], payload["content"])

#     def test_update_a_ticket_as_a_not_owner(self):
#         """a ticket update test as a not ticket owner foreign user."""
#         payload = {"content": "updated"}
#         self.client.force_authenticate(self.normal_user2)
#         url = generate_ticket_test_url(self.ticket)
#         res = self.client.patch(url, payload, "json")
#         self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

#     # def test_list_tickets_as_a_company_staff(self):
#     #     """retrive list of tickets as a company staff"""
#     #     url = generate_ticket_test_url()

