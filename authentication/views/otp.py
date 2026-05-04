from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.exceptions import EmailNotFound
from authentication.serializers import CodeGenerateSerializer, CodeLoginSerializer
from authentication.services import (
    create_user,
    delete_code,
    mark_user_verified,
    update_user_login_metadata,
    verify_code,
)
from authentication.services.user import get_user_by_email
from authentication.tasks import send_otp_email_task
from authentication.utils import get_client_ip


class CodeGenerateEndpoint(GenericAPIView):
    """Sends a one-time confirmation code to the given email address."""

    serializer_class = CodeGenerateSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        send_otp_email_task.delay(email)

        return Response(
            {
                "message": f"Confirmation code has been sent to {email}.",
            },
            status=status.HTTP_200_OK,
        )


class CodeLoginEndpoint(GenericAPIView):
    """Authenticates a user via OTP and returns JWT access and refresh tokens.

    A new account is automatically created if no user exists with the given email.
    """

    serializer_class = CodeLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        verify_code(code, email)
        delete_code(email)

        try:
            user = get_user_by_email(email)
        except EmailNotFound:
            user = create_user(email)
            mark_user_verified(user)

        # Update tracking fields
        ip_address = get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT")
        update_user_login_metadata(user, ip_address, user_agent)

        # Generate refresh and access token
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "email": user.email,
                    "display_name": user.display_name,
                },
            },
            status=status.HTTP_200_OK,
        )
