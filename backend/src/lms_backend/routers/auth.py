"""Router for authentication endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from lms_backend.auth import create_access_token, get_current_user, get_session
from lms_backend.models.user import (
    Token,
    User,
    UserCreate,
    UserRead,
    hash_password,
    verify_password,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=UserRead, status_code=201)
async def register(body: UserCreate, session: AsyncSession = Depends(get_session)):
    """Register a new user."""
    result = await session.exec(select(User).where(User.email == body.email))
    existing_user = result.one_or_none()
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Email already registered",
        )
    user = User(email=body.email, hashed_password=hash_password(body.password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    logger.info(
        "user_registered", extra={"event": "user_registered", "user_id": user.id}
    )
    return user


@router.post("/login", response_model=Token)
async def login(body: UserCreate, session: AsyncSession = Depends(get_session)):
    """Login and get access token."""
    result = await session.exec(select(User).where(User.email == body.email))
    user = result.one_or_none()
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if user.id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found",
        )
    access_token = create_access_token(data={"sub": user.id})
    logger.info(
        "user_logged_in",
        extra={
            "event": "user_logged_in",
            "user_id": user.id,
            "token_prefix": access_token[:20],
        },
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserRead)
async def get_me(user: User = Depends(get_current_user)):
    """Get current user info."""
    return user
