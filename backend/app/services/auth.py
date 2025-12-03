"""
Authentication service.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import UserCreate
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import UnauthorizedException, ConflictException


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        if self.get_user_by_email(user_data.email):
            raise ConflictException("Email already registered")

        user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=get_password_hash(user_data.password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> User:
        """Authenticate user with email and password."""
        user = self.get_user_by_email(email)
        if not user:
            raise UnauthorizedException("Invalid email or password")
        if not verify_password(password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedException("Account is disabled")

        # Update last login
        user.last_login_at = datetime.utcnow()
        self.db.commit()

        return user

