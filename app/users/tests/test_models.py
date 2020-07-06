"company_admin app models test."
from django.test import TestCase
from django.contrib.auth import get_user_model


class UserModelTests(TestCase):
    """custom user model tests"""

    def test_create_user(self):
        """normal user creation method test"""
        user = get_user_model().objects.create_user(
            email="test@test.com", password="supersecret"
        )
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.is_active, True)
        self.assertEqual(user.is_company_admin, False)
        self.assertEqual(user.is_approved, False)
        self.assertTrue(user.check_password("supersecret"))

    def test_create_company_admin_user(self):
        "company admin user creation method test"
        company_admin = get_user_model().objects.create_company_admin(
            email="test@test.com", password="supersecret"
        )
        self.assertEqual(company_admin.is_staff, True)
        self.assertEqual(company_admin.is_active, False)
        self.assertEqual(company_admin.is_company_admin, True)
        self.assertEqual(company_admin.is_approved, False)
        self.assertTrue(company_admin.check_password("supersecret"))

    def test_profile_create(self):
        "automatic creation test of profile when user approve accounts"
        user = get_user_model().objects.create_staff_user(
            email="test@test.com", password="supersecret", is_approved=True
        )
        self.assertTrue(hasattr(user, "profile"))

    def test_no_profile_owned_normal_user(self):
        "test that normal users will not have profiles."
        user = get_user_model().objects.create_user(
            email="test@test.com", password="normal", is_approved=True
        )
        self.assertFalse(hasattr(user, "profile"))
