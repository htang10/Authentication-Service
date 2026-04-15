from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.exceptions import EmailVerificationError
from authentication.serializers import ResendVerificationSerializer
from authentication.services import send_email_verification_link, verify_token


class VerifyEmailEndpoint(APIView):
    """Endpoint for verifying user email"""

    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get("token")
        purpose = request.query_params.get("purpose")

        verify_token(token, purpose)

        return Response(
            {"message": "Email verified successfully."}, status=status.HTTP_200_OK
        )


class ResendVerificationEndpoint(GenericAPIView):
    """Endpoint for resending verification email"""

    serializer_class = ResendVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        try:
            send_email_verification_link(user)
        except EmailVerificationError:
            raise APIException(
                {"error": "Failed to send verification email. Please try again later."}
            )

        return Response(
            {"message": f"A verification email has been sent to {user.email}."},
            status=status.HTTP_200_OK,
        )
