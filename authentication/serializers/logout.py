from rest_framework import serializers


class LogoutSerializer(serializers.Serializer):
    """
    Serializer for logout

    Blacklists refresh token after logout
    """

    refresh = serializers.CharField()
