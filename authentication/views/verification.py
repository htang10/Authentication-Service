from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.exceptions import EmailVerificationError
from authentication.models import Token
from authentication.serializers import ResendVerificationSerializer
from authentication.services import mark_user_verified, verify_token
from authentication.tasks import send_email_verification_link_task


class VerifyTokenEndpoint(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get("token")
        purpose = request.query_params.get("purpose")

        token_obj = verify_token(token, purpose)
        if purpose != Token.Purpose.PASSWORD_RESET:
            mark_user_verified(token_obj.user)

        return Response(
            {"message": "Verified successfully."}, status=status.HTTP_200_OK
        )


class ResendVerificationEndpoint(GenericAPIView):
    serializer_class = ResendVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        send_email_verification_link_task.delay(user.id)

        return Response(
            {"message": f"A verification email has been sent to {user.email}."},
            status=status.HTTP_200_OK,
        )
