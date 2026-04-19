from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.authentication import authenticate

from authentication.exceptions import (
    EmailAlreadyExists,
    EmailNotVerified,
    InvalidCredentials,
)
from authentication.models import User
from authentication.services import create_user, find_existing_user
from authentication.utils import normalize_email


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "display_name", "created_at", "updated_at"]
        read_only_fields = ["display_name", "created_at", "updated_at"]
        extra_kwargs = {
            "email": {"validators": []},
            "password": {
                "write_only": True,
                "style": {"input_type": "password"},
            },
        }

    def validate(self, data):
        email = normalize_email(data["email"])

        user = find_existing_user(email)
        if user:
            raise EmailAlreadyExists

        validate_password(data["password"])
        return data

    def create(self, validated_data):
        return create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, data):
        email = normalize_email(data["email"])
        user = authenticate(username=email, password=data["password"])

        if not user:
            raise InvalidCredentials

        user_obj = User.objects.get(email=email)
        if not user_obj.email_verified_at:
            raise EmailNotVerified

        data["user"] = user
        return data
