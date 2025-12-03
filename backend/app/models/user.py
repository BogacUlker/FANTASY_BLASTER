"""
User model for authentication and authorization.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.database import Base


class UserTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    # Subscription tier
    tier = Column(Enum(UserTier), default=UserTier.FREE)

    # Rate limiting
    api_calls_today = Column(Integer, default=0)
    api_calls_reset_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<User {self.username}>"
