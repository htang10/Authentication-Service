import secrets
from datetime import timedelta

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from authentication.models import Token, User
from authentication.services.tokens import hash_secret
from authentication.utils import convert_expiry


def generate_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    hashed_token = hash_secret(token)
    return token, hashed_token


def save_token(
    hashed_token_str: str, user: User, purpose: Token.Purpose, expiry: int | float
) -> None:
    hours, minutes = convert_expiry(expiry)
    expires_at = timezone.now() + timedelta(hours=hours, minutes=minutes)

    Token.objects.create(
        user=user, token=hashed_token_str, purpose=purpose, expires_at=expires_at
    )


def verify_token(token_str: str, purpose: Token.Purpose) -> Token:
    if not token_str or not purpose:
        raise ValidationError("Missing credentials.")
    hashed_token = hash_secret(token_str)
    token_obj = (
        Token.objects.select_related("user")
        .filter(
            token=hashed_token,
            purpose=purpose,
            used_at__isnull=True,
            expires_at__gt=timezone.now(),
        )
        .first()
    )

    if not token_obj:
        raise ValidationError("Invalid or expired token.")

    if purpose == Token.Purpose.SIGN_UP:
        mark_used_token(token_obj)

    return token_obj


def mark_used_token(token: Token) -> None:
    token.used_at = timezone.now()
    token.save()


def invalidate_past_tokens(user: User, purpose: Token.Purpose) -> None:
    Token.objects.filter(user=user, purpose=purpose, used_at__isnull=True).update(
        expires_at=timezone.now()
    )
