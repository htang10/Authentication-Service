from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from authentication.views import (
    ForgotPasswordEndpoint,
    LoginEndpoint,
    LogoutEndpoint,
    ResendVerificationEndpoint,
    ResetPasswordEndpoint,
    SignUpEndpoint,
    VerifyTokenEndpoint,
)

urlpatterns = [
    # Email/password
    path("signup/", SignUpEndpoint.as_view(), name="signup"),
    path("login/", LoginEndpoint.as_view(), name="login"),
    path("verify/", VerifyTokenEndpoint.as_view(), name="verify"),
    path(
        "resend-verification/",
        ResendVerificationEndpoint.as_view(),
        name="resend-verification",
    ),
    # Logout
    path("logout/", LogoutEndpoint.as_view(), name="logout"),
    # Password management
    path("forgot-password/", ForgotPasswordEndpoint.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordEndpoint.as_view(), name="reset-password"),
    # Auth token
    path("get-access-token/", TokenRefreshView.as_view(), name="get-access-token"),
]
