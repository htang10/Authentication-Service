import hmac
import secrets
from datetime import timedelta

from rest_framework.exceptions import ValidationError

from authentication.services.redis import redis_instance
from authentication.services.tokens import hash_secret
from authentication.utils import convert_expiry

r = redis_instance()


def generate_code(length: int = 6) -> tuple[str, str]:
    code = "".join([str(secrets.randbelow(10)) for _ in range(length)])
    hashed_code = hash_secret(code)
    return code, hashed_code


def save_code(hashed_code: str, email: str, expiry: int | float) -> None:
    hours, minutes = convert_expiry(expiry)
    r.setex(email, timedelta(hours=hours, minutes=minutes), hashed_code)


def verify_code(code: str, email: str) -> None:
    hashed_input = hash_secret(code)
    stored = r.get(email)

    if not stored or not hmac.compare_digest(hashed_input, stored):
        raise ValidationError("Invalid or expired code.")


def delete_code(email: str) -> None:
    r.delete(email)
