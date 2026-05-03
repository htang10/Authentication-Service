import hmac
import secrets
from datetime import timedelta

from authentication.exceptions import InvalidToken
from authentication.services.redis import redis_instance
from authentication.services.tokens import hash_secret
from authentication.utils import convert_expiry

r = redis_instance()


def generate_code(length: int = 6) -> tuple[str, str]:
    """Generates a numeric OTP and returns it as a (plain, hashed) tuple."""
    code = "".join([str(secrets.randbelow(10)) for _ in range(length)])
    hashed_code = hash_secret(code)
    return code, hashed_code


def save_code(hashed_code: str, email: str, expiry: int | float) -> None:
    """Stores the hashed OTP in Redis keyed by email with the given expiry."""
    hours, minutes = convert_expiry(expiry)
    r.setex(email, timedelta(hours=hours, minutes=minutes), hashed_code)


def verify_code(code: str, email: str) -> None:
    """Validates the OTP against the stored hash using a timing-safe comparison.

    Raises:
        InvalidToken: The OTP is missing or incorrect.
    """
    hashed_input = hash_secret(code)
    # `decode_responses=True` ensures string output at runtime.
    # More details at `authentication/services/redis.py`
    stored: str | None = r.get(email)  # type: ignore

    if stored is None or not hmac.compare_digest(hashed_input, stored):
        raise InvalidToken


def delete_code(email: str) -> None:
    r.delete(email)
