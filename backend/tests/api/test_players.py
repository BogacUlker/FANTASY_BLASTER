"""
Tests for player endpoints.
"""


class TestListPlayers:
    """Tests for listing players."""

    def test_list_players_success(self, client, test_player):
        """Test listing players (public endpoint)."""
        response = client.get("/api/v1/players")
        assert response.status_code == 200
        data = response.json()
        assert "players" in data
        assert "total" in data
        assert len(data["players"]) >= 1

    def test_list_players_filter_by_team(self, client, test_player):
        """Test filtering players by team."""
        response = client.get(f"/api/v1/players?team={test_player.team_abbreviation}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["players"]) == 1
        assert data["players"][0]["team_abbreviation"] == test_player.team_abbreviation

    def test_list_players_search(self, client, test_player):
        """Test searching players by name."""
        response = client.get("/api/v1/players?query=LeBron")
        assert response.status_code == 200
        data = response.json()
        assert len(data["players"]) == 1
        assert "LeBron" in data["players"][0]["full_name"]

    def test_list_players_pagination(self, client, test_player):
        """Test player listing pagination."""
        response = client.get("/api/v1/players?page=1&per_page=10")
        assert response.status_code == 200
        data = response.json()
        assert "players" in data
        assert "total" in data


class TestGetPlayer:
    """Tests for getting single player."""

    def test_get_player_success(self, client, test_player):
        """Test getting a player by ID (public endpoint)."""
        response = client.get(f"/api/v1/players/{test_player.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_player.id
        assert data["full_name"] == test_player.full_name

    def test_get_player_not_found(self, client):
        """Test getting non-existent player."""
        response = client.get("/api/v1/players/99999")
        assert response.status_code == 404


class TestPlayerStats:
    """Tests for player statistics."""

    def test_get_player_stats_empty(self, client, test_player):
        """Test getting stats for player with no games."""
        response = client.get(f"/api/v1/players/{test_player.id}/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["recent_games"] == []

    def test_get_player_stats_not_found(self, client):
        """Test getting stats for non-existent player."""
        response = client.get("/api/v1/players/99999/stats")
        assert response.status_code == 404


class TestPlayerAutocomplete:
    """Tests for player autocomplete."""

    def test_autocomplete_success(self, client, test_player):
        """Test player autocomplete search (public endpoint)."""
        response = client.get("/api/v1/players/search/autocomplete?q=Leb")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any("LeBron" in p["full_name"] for p in data)

    def test_autocomplete_no_results(self, client):
        """Test autocomplete with no matches."""
        response = client.get("/api/v1/players/search/autocomplete?q=XYZ123")
        assert response.status_code == 200
        data = response.json()
        assert data == []
