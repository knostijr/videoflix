"""Utility functions for authentication cookies and email sending."""

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def set_auth_cookies(response, access_token, refresh_token):
    """
    Set JWT access and refresh tokens as HttpOnly cookies on the response.

    Args:
        response: The DRF Response object to attach cookies to.
        access_token: The JWT access token object.
        refresh_token: The JWT refresh token object.
    """
    jwt_settings = settings.SIMPLE_JWT
    response.set_cookie(
        key=jwt_settings['AUTH_COOKIE'],
        value=str(access_token),
        httponly=jwt_settings['AUTH_COOKIE_HTTP_ONLY'],
        secure=jwt_settings['AUTH_COOKIE_SECURE'],
        samesite=jwt_settings['AUTH_COOKIE_SAMESITE'],
        max_age=int(
            jwt_settings['ACCESS_TOKEN_LIFETIME'].total_seconds()
        ),
    )
    response.set_cookie(
        key=jwt_settings['AUTH_COOKIE_REFRESH'],
        value=str(refresh_token),
        httponly=jwt_settings['AUTH_COOKIE_HTTP_ONLY'],
        secure=jwt_settings['AUTH_COOKIE_SECURE'],
        samesite=jwt_settings['AUTH_COOKIE_SAMESITE'],
        max_age=int(
            jwt_settings['REFRESH_TOKEN_LIFETIME'].total_seconds()
        ),
    )


def delete_auth_cookies(response):
    """
    Delete JWT cookies from the response to log the user out.

    Args:
        response: The DRF Response object to remove cookies from.
    """
    response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
    response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])


def build_activation_url(request, uid, token):
    """
    Build the frontend activation URL containing the uid and token.

    Args:
        request: The HTTP request.
        uid (str): Base64-encoded user ID.
        token (str): The activation token.

    Returns:
        str: The complete frontend activation URL.
    """
    frontend_url = settings.FRONTEND_URL
    return (
        f"{frontend_url}/pages/auth/activate.html"
        f"?uid={uid}&token={token}"
    )


def build_password_reset_url(uid, token):
    """
    Build the frontend password reset URL containing the uid and token.

    Args:
        uid (str): Base64-encoded user ID.
        token (str): The password reset token.

    Returns:
        str: The complete frontend password reset URL.
    """
    frontend_url = settings.FRONTEND_URL
    return (
        f"{frontend_url}/pages/auth/confirm_password.html"
        f"?uid={uid}&token={token}"
    )


def send_activation_email(request, user):
    """
    Send an account activation email with a tokenised link to the user.

    Args:
        request: The HTTP request used to build the activation URL.
        user (CustomUser): The newly registered user.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_url = build_activation_url(request, uid, token)
    context = {'user': user, 'activation_url': activation_url}
    html_content = render_to_string('emails/activation.html', context)
    email = EmailMultiAlternatives(
        subject='Videoflix – Activate your account',
        body=f'Activate your account: {activation_url}',
        to=[user.email],
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()


def send_password_reset_email(user):
    """
    Send a password reset email with a tokenised link to the user.

    Args:
        user (CustomUser): The user who requested the reset.
    """
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_url = build_password_reset_url(uid, token)
    context = {'user': user, 'reset_url': reset_url}
    html_content = render_to_string('emails/password_reset.html', context)
    email = EmailMultiAlternatives(
        subject='Videoflix – Reset your password',
        body=f'Reset your password: {reset_url}',
        to=[user.email],
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()
