"""Tests for the user registration endpoint."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from tests.base import VideoflixTestCase, UserFactory

User = get_user_model()


class RegisterViewTest(VideoflixTestCase):
    """Test suite for POST /api/register/."""

    def setUp(self):
        """Set up the URL and a valid payload for each test."""
        super().setUp()
        self.url = reverse('register')
        self.valid_payload = {
            'email': 'newuser@example.com',
            'password': 'securepassword123',
            'confirmed_password': 'securepassword123',
        }

    def test_register_with_valid_data_returns_201(self):
        """A valid registration payload should return HTTP 201."""
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_creates_inactive_user(self):
        """A newly registered user must be inactive until email activation."""
        self.client.post(self.url, self.valid_payload)
        user = User.objects.get(email='newuser@example.com')
        self.assertFalse(user.is_active)

    def test_register_with_duplicate_email_returns_400(self):
        """Registration with an already existing email should return 400."""
        UserFactory(email='existing@example.com')
        payload = {**self.valid_payload, 'email': 'existing@example.com'}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_mismatched_passwords_returns_400(self):
        """Mismatched password fields should return HTTP 400."""
        payload = {**self.valid_payload, 'confirmed_password': 'different'}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_missing_email_returns_400(self):
        """A payload missing the email field should return HTTP 400."""
        payload = {
            'password': 'securepassword123',
            'confirmed_password': 'securepassword123',
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_error_message_does_not_reveal_existing_email(self):
        """
        Error messages must not disclose whether an email already exists.

        This prevents user enumeration attacks where an attacker probes
        the API to build a list of registered email addresses.
        """
        UserFactory(email='existing@example.com')
        payload = {**self.valid_payload, 'email': 'existing@example.com'}
        response = self.client.post(self.url, payload)
        self.assertNotIn('existing', str(response.data).lower())
