from rest_framework import serializers
from rest_framework.authentication import authenticate

from authentication.exceptions import EmailNotVerified, InvalidCredentials
from authentication.models import User
from authentication.services import create_user
from authentication.utils import normalize_email


class SignUpSerializer(serializers.ModelSerializer):
    """
    Serializer for sign-up

    Creates new user account if email has not been registered yet
    Hashes password before storing user in db
    """

    class Meta:
        model = User
        fields = ["email", "password", "display_name", "created_at", "updated_at"]
        read_only_fields = ["display_name", "created_at", "updated_at"]
        extra_kwargs = {
            "password": {
                "min_length": 8,
                "write_only": True,
                "style": {"input_type": "password"},
            }
        }

    def create(self, validated_data):
        return create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """
    Serializer for login

    Checks for existing verified email and correct password
    """

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
