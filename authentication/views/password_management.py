from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from authentication.serializers import ForgotPasswordSerializer, ResetPasswordSerializer
from authentication.services import reset_password, send_password_reset_link


class ForgotPasswordEndpoint(GenericAPIView):
    """Validate user and send password reset link"""

    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        send_password_reset_link(user)

        return Response(
            {"message": f"A password reset link has been sent to {user.email}."},
            status=status.HTTP_200_OK,
        )


class ResetPasswordEndpoint(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        reset_password(token, new_password)

        return Response(
            {"message": f"Password has been changed."},
            status=status.HTTP_200_OK,
        )
