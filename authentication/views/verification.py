from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from authentication.exceptions import EmailVerificationError
from authentication.serializers import ResendVerificationSerializer
from authentication.services import verify_token, handle_email_verification


class VerifyEmailEndpoint(APIView):
    """Endpoint for verifying user email"""
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get("token")

        verify_token(token)

        return Response({
            "message": "Email verified successfully."
        }, status=status.HTTP_200_OK)


class ResendVerificationEndpoint(GenericAPIView):
    """Endpoint for resending verification email"""
    serializer_class = ResendVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        try:
            handle_email_verification(user)
        except EmailVerificationError:
            raise APIException({"error": "Failed to send verification email. Please try again later."})

        return Response({
            "message": f"A verification email has been sent to {user.email}."
        }, status=status.HTTP_200_OK)