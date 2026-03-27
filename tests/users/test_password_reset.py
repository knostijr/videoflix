"""Tests for the password reset flow."""

from django.urls import reverse
from rest_framework import status

from tests.base import VideoflixTestCase, UserFactory


class PasswordResetViewTest(VideoflixTestCase):
    """Test suite for POST /api/password_reset/."""

    def setUp(self):
        """Set up the URL and a registered user."""
        super().setUp()
        self.url = reverse('password-reset')
        self.user = UserFactory(email='reset@example.com')

    def test_reset_with_existing_email_returns_200(self):
        """A reset request for an existing email should return HTTP 200."""
        response = self.client.post(
            self.url, {'email': 'reset@example.com'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_with_nonexistent_email_still_returns_200(self):
        """
        A reset request for an unknown email must also return 200.

        Returning 404 for unknown emails would allow attackers to check
        which email addresses are registered (user enumeration).
        """
        response = self.client.post(
            self.url, {'email': 'nobody@example.com'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reset_response_is_identical_for_known_and_unknown_email(self):
        """
        The response body must be identical 
        regardless of email existence.
        """
        response_known = self.client.post(
            self.url, {'email': 'reset@example.com'}
        )
        response_unknown = self.client.post(
            self.url, {'email': 'nobody@example.com'}
        )
        self.assertEqual(response_known.data, response_unknown.data)
