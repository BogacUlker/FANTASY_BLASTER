"""
Authentication endpoints.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    TokenRefresh,
)
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.core.exceptions import ConflictException, UnauthorizedException
from app.api.v1.dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> User:
    """Register a new user."""
    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise ConflictException(detail="Email already registered")

    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise ConflictException(detail="Username already taken")

    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
) -> Token:
    """Authenticate user and return tokens."""
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise UnauthorizedException(detail="Incorrect email or password")

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated",
        )

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db),
) -> Token:
    """Refresh access token using refresh token."""
    payload = decode_refresh_token(token_data.refresh_token)

    if payload is None:
        raise UnauthorizedException(detail="Invalid refresh token")

    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException(detail="Invalid refresh token")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise UnauthorizedException(detail="User not found or inactive")

    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current user information."""
    return current_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Logout user (client should discard tokens)."""
    # In a production system, you might want to blacklist the token
    return {"message": "Successfully logged out"}
