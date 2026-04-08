"""Database operations for users."""

import logging

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from lms_backend.models.user import User

logger = logging.getLogger(__name__)


async def read_user_by_email(session: AsyncSession, email: str) -> User | None:
    """Read a user by email."""
    result = await session.exec(select(User).where(User.email == email))
    return result.one_or_none()


async def read_user(session: AsyncSession, user_id: int) -> User | None:
    """Read a user by id."""
    return await session.get(User, user_id)
