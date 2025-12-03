"""
Tests for authentication endpoints.
"""
import pytest


class TestRegister:
    """Tests for user registration."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "securepassword123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "id" in data
        assert "password_hash" not in data

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with existing email fails."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "anotheruser",
                "password": "newpassword123",
            },
        )
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client):
        """Test registration with invalid email fails."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "username": "testuser2",
                "password": "securepassword123",
            },
        )
        assert response.status_code == 422

    def test_register_weak_password(self, client):
        """Test registration with weak password fails."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "testuser3",
                "password": "123",
            },
        )
        assert response.status_code == 422


class TestLogin:
    """Tests for user login."""

    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password fails."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email fails."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "somepassword",
            },
        )
        assert response.status_code == 401


class TestMe:
    """Tests for current user endpoint."""

    def test_get_me_authenticated(self, authorized_client, test_user):
        """Test getting current user when authenticated."""
        response = authorized_client.get("/api/v1/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username

    def test_get_me_unauthenticated(self, client):
        """Test getting current user without authentication."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401


class TestRefreshToken:
    """Tests for token refresh endpoint."""

    def test_refresh_token_success(self, client, test_user, db):
        """Test successful token refresh."""
        # First login to get tokens
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123",
            },
        )
        tokens = login_response.json()

        # Refresh the token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token fails."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token"},
        )
        assert response.status_code == 401
