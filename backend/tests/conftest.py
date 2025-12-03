"""
Pytest configuration and fixtures.
"""
import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserTier
from app.models.team import Team
from app.models.player import Player, InjuryStatus
from app.core.security import get_password_hash, create_access_token

# Test database URL (in-memory SQLite for tests)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database override."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True,
        tier=UserTier.FREE,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user_token(test_user) -> str:
    """Create an access token for the test user."""
    return create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
def authorized_client(client, test_user_token):
    """Create a test client with authorization header."""
    client.headers["Authorization"] = f"Bearer {test_user_token}"
    return client


@pytest.fixture
def test_team(db) -> Team:
    """Create a test team."""
    team = Team(
        nba_team_id="1610612747",
        name="Los Angeles Lakers",
        abbreviation="LAL",
        city="Los Angeles",
        conference="Western",
        division="Pacific",
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@pytest.fixture
def test_player(db, test_team) -> Player:
    """Create a test player."""
    player = Player(
        nba_player_id="2544",
        name="LeBron James",
        position="SF",
        height="6-9",
        weight=250,
        birth_date=date(1984, 12, 30),
        team_id=test_team.id,
        injury_status=InjuryStatus.HEALTHY,
        is_active=True,
    )
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


@pytest.fixture
def pro_user(db) -> User:
    """Create a pro tier user."""
    user = User(
        email="pro@example.com",
        hashed_password=get_password_hash("propassword123"),
        full_name="Pro User",
        is_active=True,
        tier=UserTier.PRO,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db) -> User:
    """Create an admin user."""
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword123"),
        full_name="Admin User",
        is_active=True,
        is_superuser=True,
        tier=UserTier.PREMIUM,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
