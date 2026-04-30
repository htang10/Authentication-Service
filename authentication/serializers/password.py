from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from authentication.utils import normalize_email


class SignUpSerializer(serializers.Serializer):
    """Validates password-based sign-up inputs.

    Attributes:
        email: Normalized to lowercase before validation.
        password: Validated against Django's password validators.

    Raises:
        ValidationError: Either email format is invalid or password fails strength requirements.
    """

    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, data):
        data["email"] = normalize_email(data["email"])
        validate_password(data["password"])
        return data


class LoginSerializer(serializers.Serializer):
    """Validates password-based login credentials.

    Attributes:
        email: Normalized to lowercase before validation.

    Raises:
        ValidationError: Invalid email format.
    """

    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, data):
        data["email"] = normalize_email(data["email"])
        return data
