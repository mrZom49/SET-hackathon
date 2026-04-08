"""Models for users and authentication."""

import bcrypt
from datetime import datetime, timezone
from pydantic import Field
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """A user in the flashcard application."""

    __tablename__ = "user"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    hashed_password: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )


class UserCreate(SQLModel):
    """Schema for creating a user."""

    email: str
    password: str


class UserRead(SQLModel):
    """Schema for reading a user."""

    id: int
    email: str
    created_at: datetime


class Token(SQLModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )
