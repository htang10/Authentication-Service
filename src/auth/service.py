from fastapi import HTTPException, status

from ..database import SessionDep
from .mailing import send_verification_email
from .models import User
from .repository import email_exists
from .security import hash_password, generate_ott, hash_token
from .utils import generate_username


async def register_user(email: str, password: str, session: SessionDep) -> User:
    email = email.lower() # Normalize email
    if email_exists(email, session):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The provided email is already registered with an existing account."
        )
    hashed_password = hash_password(password)
    username = await generate_username(session)

    user = User(email=email, hashed_password=hashed_password, username=username.lower())
    session.add(user)
    session.commit()
    session.refresh(user)

    token = generate_ott()
    hashed_token = hash_token(token)
    send_verification_email(email, token)

    return user

