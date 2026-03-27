"""Shared base class and factories for all Videoflix tests."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

import factory

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating active test users with sensible defaults."""

    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'user{n}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True


class InactiveUserFactory(UserFactory):
    """Factory for creating inactive (unactivated) test users."""

    is_active = False


class VideoflixTestCase(TestCase):
    """
    Base test case for all Videoflix tests.

    Provides a pre-configured API client and a helper method
    to authenticate requests without going through the login endpoint.
    """

    def setUp(self):
        """Set up the API client before each test."""
        self.client = APIClient()

    def authenticate(self, user):
        """
        Force-authenticate the API client as the given user.

        This bypasses the login endpoint and JWT middleware entirely.
        It tests business logic in isolation, not the auth mechanism itself.

        Args:
            user (CustomUser): The user to authenticate as.
        """
        self.client.force_authenticate(user=user)
