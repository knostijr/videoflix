"""Custom JWT authentication reading tokens from HttpOnly cookies."""

from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """
    JWT authentication backend that reads the token from an HttpOnly cookie
    instead of the standard Authorization header.

    This prevents XSS attacks because JavaScript cannot access
    HttpOnly cookies, even if malicious code runs on the page.
    """

    def authenticate(self, request):
        """
        Authenticate the request using the JWT from the cookie.

        Args:
            request: The incoming HTTP request.

        Returns:
            tuple | None: (user, token) if valid, None if no token found.
        """
        raw_token = request.COOKIES.get(
            settings.SIMPLE_JWT['AUTH_COOKIE']
        )
        if raw_token is None:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token