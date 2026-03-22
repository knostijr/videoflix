"""Tests for the login and logout endpoints."""

from django.urls import reverse
from rest_framework import status

from tests.base import VideoflixTestCase, UserFactory, InactiveUserFactory


class LoginViewTest(VideoflixTestCase):
    """Test suite for POST /api/login/."""

    def setUp(self):
        """Set up the URL and a valid active user."""
        super().setUp()
        self.url = reverse('login')
        self.user = UserFactory(email='active@example.com')

    def test_login_with_valid_credentials_returns_200(self):
        """Valid credentials should return HTTP 200."""
        payload = {'email': 'active@example.com', 'password': 'testpass123'}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_sets_access_token_cookie(self):
        """Successful login must set an access_token HttpOnly cookie."""
        payload = {'email': 'active@example.com', 'password': 'testpass123'}
        response = self.client.post(self.url, payload)
        self.assertIn('access_token', response.cookies)

    def test_login_sets_refresh_token_cookie(self):
        """Successful login must set a refresh_token HttpOnly cookie."""
        payload = {'email': 'active@example.com', 'password': 'testpass123'}
        response = self.client.post(self.url, payload)
        self.assertIn('refresh_token', response.cookies)

    def test_login_with_wrong_password_returns_400(self):
        """Wrong password should return HTTP 400."""
        payload = {'email': 'active@example.com', 'password': 'wrongpassword'}
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inactive_user_cannot_login(self):
        """An unactivated account must be rejected with HTTP 400."""
        InactiveUserFactory(email='inactive@example.com')
        payload = {
            'email': 'inactive@example.com',
            'password': 'testpass123',
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutViewTest(VideoflixTestCase):
    """Test suite for POST /api/logout/."""

    def setUp(self):
        """Set up the URL and authenticate a test user."""
        super().setUp()
        self.url = reverse('logout')
        self.user = UserFactory()
        self.authenticate(self.user)

    def test_logout_returns_200(self):
        """An authenticated logout request should return HTTP 200."""
        self.client.cookies['refresh_token'] = 'fake-token'
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_logout_returns_401(self):
        """An unauthenticated logout request must return HTTP 401."""
        self.client.logout()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)