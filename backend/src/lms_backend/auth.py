"""API key authentication dependency."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from lms_backend.database import get_session
from lms_backend.models.user import User
from lms_backend.settings import settings

logger = logging.getLogger(__name__)

security = HTTPBearer()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7


def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Verify the API key from the Authorization header.

    Expects: Authorization: Bearer <API_KEY>
    Returns the key string if valid.
    Raises 401 if invalid.
    """
    if credentials.credentials != settings.api_key:
        logger.warning("auth_failure", extra={"event": "auth_failure"})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    logger.info("auth_success", extra={"event": "auth_success"})
    return credentials.credentials


def create_access_token(data: dict[str, int]) -> str:
    """Create a JWT access token."""
    to_encode: dict[str, int | datetime] = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        user_id: int | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await session.exec(select(User).where(User.id == user_id))
    user = result.one_or_none()
    if user is None:
        raise credentials_exception
    return user


UserDep = Annotated[User, Depends(get_current_user)]
