from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from authentication.serializers import LogoutSerializer
from authentication.services import (
    get_user_by_refresh_token,
    update_user_logout_metadata,
)
from authentication.utils import get_client_ip


class LogoutEndpoint(GenericAPIView):
    """Logout endpoint for all auth methods"""

    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        try:
            # Retrieve the owner
            user = get_user_by_refresh_token(refresh_token)
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            raise ValidationError("Token is invalid or already blacklisted.")

        ip_address = get_client_ip(request)
        update_user_logout_metadata(user, ip_address)

        return Response(status=status.HTTP_204_NO_CONTENT)
