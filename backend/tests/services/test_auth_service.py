"""
Tests for authentication service.
"""
import pytest
from app.services.auth import AuthService
from app.schemas.auth import UserCreate
from app.core.exceptions import UnauthorizedException, ConflictException


class TestAuthService:
    """Tests for AuthService."""

    def test_create_user_success(self, db):
        """Test successful user creation."""
        service = AuthService(db)
        user_data = UserCreate(
            email="new@example.com",
            password="securepassword123",
            full_name="New User",
        )
        user = service.create_user(user_data)
        assert user.email == "new@example.com"
        assert user.full_name == "New User"
        assert user.hashed_password != "securepassword123"

    def test_create_user_duplicate_email(self, db, test_user):
        """Test user creation with duplicate email fails."""
        service = AuthService(db)
        user_data = UserCreate(
            email="test@example.com",
            password="anotherpassword",
            full_name="Duplicate User",
        )
        with pytest.raises(ConflictException):
            service.create_user(user_data)

    def test_authenticate_success(self, db, test_user):
        """Test successful authentication."""
        service = AuthService(db)
        user = service.authenticate("test@example.com", "testpassword123")
        assert user.id == test_user.id

    def test_authenticate_wrong_password(self, db, test_user):
        """Test authentication with wrong password fails."""
        service = AuthService(db)
        with pytest.raises(UnauthorizedException):
            service.authenticate("test@example.com", "wrongpassword")

    def test_authenticate_nonexistent_user(self, db):
        """Test authentication with non-existent user fails."""
        service = AuthService(db)
        with pytest.raises(UnauthorizedException):
            service.authenticate("nonexistent@example.com", "password")

    def test_get_user_by_email(self, db, test_user):
        """Test getting user by email."""
        service = AuthService(db)
        user = service.get_user_by_email("test@example.com")
        assert user is not None
        assert user.id == test_user.id

    def test_get_user_by_email_not_found(self, db):
        """Test getting non-existent user by email."""
        service = AuthService(db)
        user = service.get_user_by_email("nonexistent@example.com")
        assert user is None

    def test_get_user_by_id(self, db, test_user):
        """Test getting user by ID."""
        service = AuthService(db)
        user = service.get_user_by_id(test_user.id)
        assert user is not None
        assert user.email == test_user.email

    def test_update_refresh_token(self, db, test_user):
        """Test updating user refresh token."""
        service = AuthService(db)
        service.update_refresh_token(test_user.id, "new-refresh-token")
        db.refresh(test_user)
        assert test_user.refresh_token == "new-refresh-token"

    def test_verify_refresh_token_success(self, db, test_user):
        """Test successful refresh token verification."""
        service = AuthService(db)
        service.update_refresh_token(test_user.id, "valid-token")
        assert service.verify_refresh_token(test_user.id, "valid-token") is True

    def test_verify_refresh_token_failure(self, db, test_user):
        """Test failed refresh token verification."""
        service = AuthService(db)
        service.update_refresh_token(test_user.id, "valid-token")
        assert service.verify_refresh_token(test_user.id, "invalid-token") is False
