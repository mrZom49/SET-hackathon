"""JWT-based authentication for users."""

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


def create_access_token(data: dict[str, int]) -> str:
    """Create a JWT access token."""
    user_id = data["sub"]
    to_encode: dict[str, str | datetime] = {"sub": str(user_id)}
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
    token = ""
    try:
        token = credentials.credentials
        print(
            f"DEBUG: token_received, prefix: {token[:20] if token else 'none'}, length: {len(token) if token else 0}"
        )
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            print("DEBUG: token_no_user_id")
            raise credentials_exception
        user_id = int(user_id_str)
        print(f"DEBUG: token_valid, user_id: {user_id}")
    except JWTError as e:
        print(f"DEBUG: token_decode_error: {e}")
        raise credentials_exception

    result = await session.exec(select(User).where(User.id == user_id))
    user = result.one_or_none()
    if user is None:
        print(f"DEBUG: user_not_found, user_id: {user_id}")
        raise credentials_exception
    return user


UserDep = Annotated[User, Depends(get_current_user)]
