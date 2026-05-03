from rest_framework import serializers

from authentication.exceptions import EmailAlreadyVerified, EmailNotFound
from authentication.models import User
from authentication.utils import normalize_email


class ResendVerificationSerializer(serializers.Serializer):
    """Validates email format before sending new verification link to user.

    Attributes:
        email: Normalized to lower case.
    """

    email = serializers.EmailField(max_length=255)

    def validate(self, data):
        data["email"] = normalize_email(data["email"])
        return data
