"""
Tests for player endpoints.
"""
import pytest


class TestListPlayers:
    """Tests for listing players."""

    def test_list_players_authenticated(self, authorized_client, test_player):
        """Test listing players when authenticated."""
        response = authorized_client.get("/api/v1/players/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1

    def test_list_players_unauthenticated(self, client, test_player):
        """Test listing players without authentication."""
        response = client.get("/api/v1/players/")
        assert response.status_code == 401

    def test_list_players_filter_by_team(self, authorized_client, test_player, test_team):
        """Test filtering players by team."""
        response = authorized_client.get(f"/api/v1/players/?team_id={test_team.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["team_id"] == test_team.id

    def test_list_players_search(self, authorized_client, test_player):
        """Test searching players by name."""
        response = authorized_client.get("/api/v1/players/?search=LeBron")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert "LeBron" in data["items"][0]["name"]

    def test_list_players_pagination(self, authorized_client, test_player):
        """Test player listing pagination."""
        response = authorized_client.get("/api/v1/players/?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


class TestGetPlayer:
    """Tests for getting single player."""

    def test_get_player_success(self, authorized_client, test_player):
        """Test getting a player by ID."""
        response = authorized_client.get(f"/api/v1/players/{test_player.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_player.id
        assert data["name"] == test_player.name

    def test_get_player_not_found(self, authorized_client):
        """Test getting non-existent player."""
        response = authorized_client.get("/api/v1/players/99999")
        assert response.status_code == 404

    def test_get_player_unauthenticated(self, client, test_player):
        """Test getting player without authentication."""
        response = client.get(f"/api/v1/players/{test_player.id}")
        assert response.status_code == 401


class TestPlayerStats:
    """Tests for player statistics."""

    def test_get_player_stats_empty(self, authorized_client, test_player):
        """Test getting stats for player with no games."""
        response = authorized_client.get(f"/api/v1/players/{test_player.id}/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    def test_get_player_stats_not_found(self, authorized_client):
        """Test getting stats for non-existent player."""
        response = authorized_client.get("/api/v1/players/99999/stats")
        assert response.status_code == 404


class TestPlayerAutocomplete:
    """Tests for player autocomplete."""

    def test_autocomplete_success(self, authorized_client, test_player):
        """Test player autocomplete search."""
        response = authorized_client.get("/api/v1/players/autocomplete?q=Leb")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any("LeBron" in p["name"] for p in data)

    def test_autocomplete_no_results(self, authorized_client):
        """Test autocomplete with no matches."""
        response = authorized_client.get("/api/v1/players/autocomplete?q=XYZ123")
        assert response.status_code == 200
        data = response.json()
        assert data == []
