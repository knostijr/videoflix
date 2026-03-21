"""Serializers for user registration, authentication and password management."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """Validate and process new user registration data."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirmed_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """
        Ensure the email address is not already registered.

        Args:
            value (str): The submitted email address.

        Returns:
            str: The validated email.

        Raises:
            ValidationError: With a generic message to prevent enumeration.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Please check your inputs and try again.'
            )
        return value

    def validate(self, data):
        """
        Ensure both password fields match.

        Args:
            data (dict): All validated field values.

        Returns:
            dict: The validated data.

        Raises:
            ValidationError: If the passwords do not match.
        """
        if data['password'] != data['confirmed_password']:
            raise serializers.ValidationError(
                'Please check your inputs and try again.'
            )
        return data

    def create(self, validated_data):
        """
        Create and return a new inactive user.

        Args:
            validated_data (dict): Cleaned registration data.

        Returns:
            CustomUser: The newly created inactive user.
        """
        validated_data.pop('confirmed_password')
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Read-only serializer for user data included in API responses."""

    class Meta:
        model = User
        fields = ['id', 'email']


class PasswordResetSerializer(serializers.Serializer):
    """Validate a password reset request containing an email address."""

    email = serializers.EmailField()


class PasswordConfirmSerializer(serializers.Serializer):
    """Validate new password data for a password reset confirmation."""

    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Ensure both new password fields match.

        Args:
            data (dict): All validated field values.

        Returns:
            dict: The validated data.

        Raises:
            ValidationError: If the passwords do not match.
        """
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError('Passwords do not match.')
        return data