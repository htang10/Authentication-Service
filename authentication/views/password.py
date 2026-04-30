from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.exceptions import EmailAlreadyExists, MailingServiceFailure
from authentication.serializers import LoginSerializer, SignUpSerializer
from authentication.services import (
    authenticate_user,
    create_user,
    find_user_by_email,
    update_user_login_metadata,
)
from authentication.tasks import send_email_verification_link_task
from authentication.utils import get_client_ip


class SignUpEndpoint(GenericAPIView):
    """Creates a new user and sends a verification link to their email address.

    The user account is created regardless of whether the verification email was sent successfully.

    Raises:
        EmailAlreadyExists: The given email has already been registered by another user.
    """

    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # Check if the email has already been registered by another user
        if find_user_by_email(email):
            raise EmailAlreadyExists
        user = create_user(email, password)

        try:
            send_email_verification_link_task.delay(user.email)
        except MailingServiceFailure:
            return Response(
                {
                    "message": "Account created but failed to send verification email.",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "message": f"Account created. A verification email has been sent to {user.email}.",
            },
            status=status.HTTP_201_CREATED,
        )


class LoginEndpoint(GenericAPIView):
    """Authenticates a user and returns JWT access and refresh tokens.

    On successful authentication, login metadata is updated with the request time, IP address, and user agent.

    Raises:
        InvalidCredentials: The provided email or password is incorrect.
        EmailNotVerified: The user's email has not been verified.
    """

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # Authenticate user
        user = authenticate_user(email, password)
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
