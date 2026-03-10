from sqlalchemy import select

from ..database import SessionDep
from .models import User


def email_exists(email: str, session: SessionDep) -> bool:
    statement = select(User).where(User.email == email)
    result = session.execute(statement).scalar()
    return result is not None


def username_exists(username: str, session: SessionDep) -> bool:
    statement = select(User).where(User.username == username.lower())
    result = session.execute(statement).scalar()
    return result is not None