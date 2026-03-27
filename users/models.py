"""Custom user model using email as the primary identifier."""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that replaces the default Django user.

    Uses email as the unique identifier instead of a username.
    A username field is included for akademie entrypoint compatibility.
    Accounts are inactive by default until email activation.
    """

    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=150, unique=True, blank=True, null=True
    )
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        """Return the user's email address as string representation."""
        return self.email
