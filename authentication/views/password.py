from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.exceptions import EmailVerificationError
from authentication.serializers import SignUpSerializer, LoginSerializer
from authentication.services import handle_email_verification, update_user_login_metadata


class SignUpEndpoint(GenericAPIView):
    """Password-based sign-up endpoint"""
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        try:
            handle_email_verification(user)
        except EmailVerificationError:
            return Response({
                "message": "Account created but verification email failed to send.",
            }, status=status.HTTP_201_CREATED)

        return Response({
            "message": f"Account created. A verification email has been sent to {user.email}.",
        }, status=status.HTTP_201_CREATED)


class LoginEndpoint(GenericAPIView):
    """Password-based login endpoint"""
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # update tracking fields
        user = update_user_login_metadata(user, request)

        # Generate refresh and access token
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "email": user.email,
                "display_name": user.display_name,
            }
        }, status=status.HTTP_200_OK)

