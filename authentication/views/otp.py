from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.serializers import CodeGenerateSerializer, CodeLoginSerializer
from authentication.services import (
    delete_code,
    mark_user_verified,
    update_user_login_metadata,
)
from authentication.tasks import send_otp_email_task
from authentication.utils import get_client_ip


class CodeGenerateEndpoint(GenericAPIView):
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
            status=status.HTTP_201_CREATED,
        )


class CodeLoginEndpoint(GenericAPIView):
    serializer_class = CodeLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Update tracking fields
        ip_address = get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT")
        update_user_login_metadata(user, ip_address, user_agent)

        # Mark user as verified if not yet done
        if not user.email_verified_at:
            mark_user_verified(user)

        delete_code(user.email)

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
