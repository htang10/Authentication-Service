from rest_framework import serializers

from authentication.exceptions import EmailNotFound, EmailAlreadyVerified
from authentication.models import User
from authentication.utils import normalize_email


class ResendVerificationSerializer(serializers.Serializer):
    """
    Serializer for resending verification email

    Only send verification to an existing and unverified account
    """
    email = serializers.EmailField(max_length=255)

    def validate(self, data):
        email = normalize_email(data["email"])

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise EmailNotFound

        if user.email_verified_at:
            raise EmailAlreadyVerified

        return {"user": user}