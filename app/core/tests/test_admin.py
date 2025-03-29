"""
Tests for the Django admin modifications.
"""
from typing import cast
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client
from core.models import UserManager


class AdminSiteTests(TestCase):
    """Test for Django admin."""

    # Not normal convention but bobian
    def setUp(self):
        """Create user and client."""
        self.client = Client()
        self.admin_user = cast(UserManager, get_user_model().objects).create_superuser(
            email='admin@example.com',
            password='testpass123',
        )
        self.client.force_login(self.admin_user)
        self.user = cast(UserManager, get_user_model().objects).create_user(
            email='user@example.com',
            password='testpass123',
            name="Test User"
        )

    def test_users_list(self):
        """Test that users are listed on page."""
        # List of users in the system
        # Will fail if never register the URL
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user page works."""
        user_id: int = cast(int, self.user.id) # type: ignore
        url = reverse('admin:core_user_change', args=[user_id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test the create user page works."""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)