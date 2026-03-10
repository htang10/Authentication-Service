import random, secrets
import string

from ..database import SessionDep
from .repository import username_exists


async def generate_username(session: SessionDep, length: int | None = None, max_attempts: int = 100) -> str:
    if length is None:
        length = random.randint(10, 32)

    characters = string.ascii_letters + string.digits + string.punctuation

    for _ in range(max_attempts):
        username = "".join(secrets.choice(characters) for _ in range(length))
        if not username_exists(username, session):
            return username

    raise RuntimeError("Unable to generate a unique username after max attempts.")