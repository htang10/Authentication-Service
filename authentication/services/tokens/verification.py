import secrets
from datetime import timedelta
from hashlib import sha512

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from authentication.models import Token, User


def generate_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    hashed_token = sha512(token.encode("utf-8")).hexdigest()
    return token, hashed_token


def save_token(
    hashed_token: str, user: User, purpose: Token.Purpose, expiry: int | float
) -> Token:
    hours = int(expiry)
    minutes = (expiry - hours) * 60
    expires_at = timezone.now() + timedelta(hours=hours, minutes=minutes)

    return Token.objects.create(
        user=user, token=hashed_token, purpose=purpose, expires_at=expires_at
    )


def verify_token(token: str, purpose: Token.Purpose):
    if not token:
        raise ValidationError({"error": "Token is required."})
    hashed_token = sha512(token.encode("utf-8")).hexdigest()
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
        raise ValidationError({"error": "Invalid or expired token."})

    token_obj.used_at = timezone.now()
    token_obj.save()

    token_obj.user.email_verified_at = timezone.now()
    token_obj.user.save()


def invalidate_past_tokens(user: User, purpose: Token.Purpose) -> None:
    Token.objects.filter(user=user, purpose=purpose, used_at__isnull=True).update(
        expires_at=timezone.now()
    )
