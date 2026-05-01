from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from authentication.utils import normalize_email


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, data):
        data["email"] = normalize_email(data["email"])
        return data


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(
        max_length=128, write_only=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        min_length=8, write_only=True, style={"input_type": "password"}
    )

    def validate(self, data):
        validate_password(data["new_password"])
        return data
