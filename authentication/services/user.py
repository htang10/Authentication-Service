from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from authentication.models import Token, User


def create_user(*, email: str, password: str, **extra_fields) -> User:
    user = User.objects.create(email=email, **extra_fields)
    user.set_password(password)
    user.save()
    return user


def get_user_by_refresh_token(token: Token) -> User:
    """Retrieves a user by refresh token"""
    user_id = RefreshToken(token)["user_id"]
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise TokenError
    return user


def update_user_login_metadata(user: User, ip_address: str, user_agent: str) -> None:
    """
    Updates the user login metadata including timestamp, ip address, user agent and medium.
    """
    now = timezone.now()
    user.last_login_time = now
    user.last_active = now
    user.last_login_ip = ip_address
    user.last_login_uagent = user_agent
    user.last_login_medium = "email"
    user.save(
        update_fields=[
            "last_login_time",
            "last_active",
            "last_login_ip",
            "last_login_uagent",
            "last_login_medium",
        ]
    )


def update_user_logout_metadata(user: User, ip_address: str) -> None:
    """
    Updates the user logout metadata including timestamp and ip address
    """
    user.last_logout_time = timezone.now()
    user.last_logout_ip = ip_address
    user.save(update_fields=["last_logout_time", "last_logout_ip"])
