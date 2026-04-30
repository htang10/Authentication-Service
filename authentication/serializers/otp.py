from rest_framework import serializers

from authentication.services import create_user, find_user_by_email, verify_code
from authentication.utils import normalize_email


class CodeGenerateSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, data):
        data["email"] = normalize_email(data["email"])
        return data


class CodeLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        email = normalize_email(data["email"])
        code = data["code"]

        verify_code(code, email)

        return {"email": email}

    def create(self, validated_data):
        user = find_user_by_email(validated_data["email"])
        if not user:
            return create_user(**validated_data)
        return user
