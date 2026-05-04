from rest_framework import serializers

from authentication.utils import normalize_email


class CodeGenerateSerializer(serializers.Serializer):
    """Validates OTP generation inputs.

    Attributes:
        email: Normalized to lowercase.
    """

    email = serializers.EmailField(max_length=255)

    def validate(self, data):
        data["email"] = normalize_email(data["email"])
        return data


class CodeLoginSerializer(serializers.Serializer):
    """Validates OTP login credentials.

    Attributes:
        email: Normalized to lowercase.
    """

    email = serializers.EmailField(max_length=255)
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        data["email"] = normalize_email(data["email"])
        return data
