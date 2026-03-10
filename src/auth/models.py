import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import List

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


def current_time_utc() -> datetime:
    return datetime.now(timezone.utc)


def token_expiry() -> datetime:
    return current_time_utc() + timedelta(hours=48)


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid7, primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, name="password")
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=current_time_utc)
    updated_at: Mapped[datetime] = mapped_column(default=current_time_utc, onupdate=current_time_utc)

    tokens: Mapped[List["Token"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan", # Handle cascading deletion at ORM level
        passive_deletes=True # Let database handle cascading deletion at its level
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} username={self.username}>"


class Token(Base):
    __tablename__ = "token"

    class TokenType(Enum):
        EMAIL_VERIFICATION = "email_verification"
        PASSWORD_RESET = "password_reset"
        REFRESH_TOKEN = "refresh_token"

    id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid7, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    token_type: Mapped[TokenType] = mapped_column(nullable=False)
    used: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=current_time_utc)
    expires_at: Mapped[datetime] = mapped_column(default=token_expiry)

    user: Mapped["User"] = relationship(back_populates="tokens")

    def __repr__(self) -> str:
        return (
            f"<Token id={self.id} "
            f"user_id={self.user_id} "
            f"token_hash={self.token_hash} "
            f"expired_at={self.expires_at}>"
        )