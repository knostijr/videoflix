"""Views for user authentication: register, activate, login, logout, reset."""

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    PasswordConfirmSerializer,
    PasswordResetSerializer,
    RegisterSerializer,
    UserSerializer,
)
from .utils import (
    delete_auth_cookies,
    send_activation_email,
    send_password_reset_email,
    set_auth_cookies,
)

User = get_user_model()


class RegisterView(APIView):
    """Handle new user registration and send an activation email."""

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Register a new inactive user and trigger an activation email.

        Args:
            request: HTTP request with email and password fields.

        Returns:
            Response: 201 with user data on success, 400 on validation error.
        """
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'detail': 'Please check your inputs and try again.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = serializer.save()
        send_activation_email(request, user)
        return Response(
            {
                'user': UserSerializer(user).data,
                'token': 'activation_email_sent',
            },
            status=status.HTTP_201_CREATED,
        )


class ActivateAccountView(APIView):
    """Activate a user account via the emailed token link."""

    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        """
        Activate the user account if the uid and token are valid.

        Args:
            request: The incoming HTTP request.
            uidb64 (str): Base64-encoded user ID from the activation link.
            token (str): Activation token from the link.

        Returns:
            Response: 200 on success, 400 if the token is invalid.
        """
        user = self._decode_user(uidb64)
        if user is None or not default_token_generator.check_token(
            user, token
        ):
            return Response(
                {'detail': 'Activation failed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.is_active = True
        user.save()
        return Response({'message': 'Account successfully activated.'})

    def _decode_user(self, uidb64):
        """
        Decode a base64 user ID and return the matching user instance.

        Args:
            uidb64 (str): The base64-encoded user ID string.

        Returns:
            CustomUser | None: The user if found, otherwise None.
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            return User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return None


class LoginView(APIView):
    """Authenticate a user and issue JWT tokens as HttpOnly cookies."""

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Log in a user and set JWT tokens as HttpOnly cookies.

        Args:
            request: HTTP request with email and password.

        Returns:
            Response: 200 with user info on success, 400 on invalid credentials.
        """
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response(
                {'detail': 'Please check your inputs and try again.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        refresh = RefreshToken.for_user(user)
        response = Response({
            'detail': 'Login successful',
            'user': UserSerializer(user).data,
        })
        set_auth_cookies(response, refresh.access_token, refresh)
        return response


class LogoutView(APIView):
    """Blacklist the refresh token and clear auth cookies."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Log out the user by blacklisting their refresh token.

        Args:
            request: The authenticated HTTP request.

        Returns:
            Response: 200 with cleared cookies, 400 if token is missing.
        """
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token missing.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self._blacklist_token(refresh_token)
        response = Response({
            'detail': (
                'Logout successful! All tokens will be deleted. '
                'Refresh token is now invalid.'
            )
        })
        delete_auth_cookies(response)
        return response

    def _blacklist_token(self, raw_token):
        """
        Add the given refresh token to the blacklist.

        Errors are silently ignored so logout always succeeds.

        Args:
            raw_token (str): The raw refresh token string.
        """
        try:
            RefreshToken(raw_token).blacklist()
        except Exception:
            pass


class TokenRefreshView(APIView):
    """Issue a new access token using the refresh token cookie."""

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Refresh the access token using the refresh token cookie.

        Args:
            request: HTTP request containing the refresh_token cookie.

        Returns:
            Response: 200 with new token, 400 if missing, 401 if invalid.
        """
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token missing.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            refresh = RefreshToken(refresh_token)
            new_access = refresh.access_token
            response = Response({
                'detail': 'Token refreshed',
                'access': str(new_access),
            })
            set_auth_cookies(response, new_access, refresh)
            return response
        except Exception:
            return Response(
                {'detail': 'Invalid refresh token.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class PasswordResetView(APIView):
    """Send a password reset email if the given address is registered."""

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Initiate a password reset. Always returns 200 to prevent enumeration.

        Args:
            request: HTTP request containing the email field.

        Returns:
            Response: Always 200 with a generic message.
        """
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self._send_reset_if_user_exists(
            serializer.validated_data['email']
        )
        return Response(
            {'detail': 'An email has been sent to reset your password.'}
        )

    def _send_reset_if_user_exists(self, email):
        """
        Send the reset email only if a user with this email exists.

        Args:
            email (str): The email address to look up.
        """
        try:
            user = User.objects.get(email=email)
            send_password_reset_email(user)
        except User.DoesNotExist:
            pass


class PasswordConfirmView(APIView):
    """Set a new password using a valid password reset token."""

    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """
        Confirm a password reset and update the user's password.

        Args:
            request: HTTP request with new_password and confirm_password.
            uidb64 (str): Base64-encoded user ID from the reset link.
            token (str): Password reset token from the reset link.

        Returns:
            Response: 200 on success, 400 on invalid token or data.
        """
        serializer = PasswordConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = self._decode_user(uidb64)
        if user is None or not default_token_generator.check_token(
            user, token
        ):
            return Response(
                {'detail': 'Invalid or expired reset link.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(
            {'detail': 'Your Password has been successfully reset.'}
        )

    def _decode_user(self, uidb64):
        """
        Decode a base64 user ID and return the matching user instance.

        Args:
            uidb64 (str): The base64-encoded user ID string.

        Returns:
            CustomUser | None: The user if found, otherwise None.
        """
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            return User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return None