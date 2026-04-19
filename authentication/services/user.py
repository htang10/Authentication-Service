from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken, Token, TokenError

from authentication.models import User


def create_user(*, email: str, password: str, **extra_fields) -> User:
    user = User.objects.create(email=email, **extra_fields)
    user.set_password(password)
    user.save()
    return user


def find_existing_user(email: str) -> User | None:
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


def get_user_by_refresh_token(token: Token) -> User:
    user_id = RefreshToken(token)["user_id"]
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise TokenError
    return user


def update_user_login_metadata(user: User, ip_address: str, user_agent: str) -> None:
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
    user.last_logout_time = timezone.now()
    user.last_logout_ip = ip_address
    user.save(update_fields=["last_logout_time", "last_logout_ip"])


def mark_user_verified(user: User) -> None:
    user.email_verified_at = timezone.now()
    user.save(update_fields=["email_verified_at"])
