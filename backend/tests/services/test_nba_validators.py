"""
Tests for NBA data validators.
"""
import pytest
from datetime import date
from app.services.nba.validators import (
    PlayerValidator,
    GameStatsValidator,
    TeamValidator,
    ValidationResult,
)


class TestPlayerValidator:
    """Tests for PlayerValidator."""

    def test_validate_valid_player(self):
        """Test validation of valid player data."""
        data = {
            "nba_player_id": "2544",
            "name": "LeBron James",
            "position": "SF",
            "height": "6-9",
            "weight": "250",
            "birth_date": "1984-12-30",
            "team_id": 1,
        }
        result = PlayerValidator.validate(data)

        assert result.is_valid
        assert len(result.errors) == 0
        assert result.cleaned_data["nba_player_id"] == "2544"
        assert result.cleaned_data["name"] == "LeBron James"
        assert result.cleaned_data["position"] == "SF"
        assert result.cleaned_data["height"] == "6-9"
        assert result.cleaned_data["weight"] == 250

    def test_validate_missing_required_fields(self):
        """Test validation fails for missing required fields."""
        data = {"position": "PG"}
        result = PlayerValidator.validate(data)

        assert not result.is_valid
        assert len(result.errors) >= 2
        assert any("nba_player_id" in e for e in result.errors)
        assert any("name" in e for e in result.errors)

    def test_validate_normalizes_height(self):
        """Test height normalization."""
        # Test "6'9\"" format
        data = {
            "nba_player_id": "123",
            "name": "Test Player",
            "height": "6'9\"",
        }
        result = PlayerValidator.validate(data)
        assert result.cleaned_data["height"] == "6-9"

    def test_validate_parses_weight(self):
        """Test weight parsing."""
        data = {
            "nba_player_id": "123",
            "name": "Test Player",
            "weight": "250 lbs",
        }
        result = PlayerValidator.validate(data)
        assert result.cleaned_data["weight"] == 250

    def test_validate_unusual_position_warns(self):
        """Test unusual position generates warning."""
        data = {
            "nba_player_id": "123",
            "name": "Test Player",
            "position": "GUARD",
        }
        result = PlayerValidator.validate(data)
        assert result.is_valid
        assert any("position" in w.lower() for w in result.warnings)


class TestGameStatsValidator:
    """Tests for GameStatsValidator."""

    def test_validate_valid_stats(self):
        """Test validation of valid game stats."""
        data = {
            "player_id": 1,
            "game_id": "0022400001",
            "game_date": date(2024, 12, 1),
            "minutes": 35.5,
            "points": 27,
            "rebounds": 7,
            "assists": 10,
            "steals": 1,
            "blocks": 1,
            "turnovers": 3,
            "field_goals_made": 10,
            "field_goals_attempted": 18,
        }
        result = GameStatsValidator.validate(data)

        assert result.is_valid
        assert len(result.errors) == 0
        assert result.cleaned_data["points"] == 27
        assert result.cleaned_data["fantasy_points"] > 0

    def test_validate_missing_required_fields(self):
        """Test validation fails for missing required fields."""
        data = {"points": 20}
        result = GameStatsValidator.validate(data)

        assert not result.is_valid
        assert len(result.errors) >= 3

    def test_validate_unusual_stats_warns(self):
        """Test unusual stat values generate warnings."""
        data = {
            "player_id": 1,
            "game_id": "0022400001",
            "game_date": "2024-12-01",
            "points": 80,  # Unusual
            "rebounds": 35,  # Unusual
        }
        result = GameStatsValidator.validate(data)

        assert result.is_valid  # Still valid, just warnings
        assert len(result.warnings) >= 2

    def test_validate_shot_consistency(self):
        """Test shot made/attempted consistency check."""
        data = {
            "player_id": 1,
            "game_id": "0022400001",
            "game_date": "2024-12-01",
            "field_goals_made": 15,
            "field_goals_attempted": 10,  # Made > Attempted
        }
        result = GameStatsValidator.validate(data)

        assert result.is_valid
        assert any("FG" in w for w in result.warnings)

    def test_fantasy_points_calculation(self):
        """Test fantasy points calculation."""
        data = {
            "player_id": 1,
            "game_id": "0022400001",
            "game_date": "2024-12-01",
            "points": 20,
            "rebounds": 10,
            "assists": 5,
            "steals": 2,
            "blocks": 1,
            "turnovers": 3,
        }
        result = GameStatsValidator.validate(data)

        # 20 + 10*1.2 + 5*1.5 + 2*3 + 1*3 - 3 = 20 + 12 + 7.5 + 6 + 3 - 3 = 45.5
        assert result.cleaned_data["fantasy_points"] == 45.5


class TestTeamValidator:
    """Tests for TeamValidator."""

    def test_validate_valid_team(self):
        """Test validation of valid team data."""
        data = {
            "nba_team_id": "1610612747",
            "name": "Los Angeles Lakers",
            "abbreviation": "LAL",
            "city": "Los Angeles",
            "conference": "Western",
            "division": "Pacific",
        }
        result = TeamValidator.validate(data)

        assert result.is_valid
        assert len(result.errors) == 0
        assert result.cleaned_data["abbreviation"] == "LAL"

    def test_validate_missing_required_fields(self):
        """Test validation fails for missing required fields."""
        data = {"city": "Los Angeles"}
        result = TeamValidator.validate(data)

        assert not result.is_valid
        assert len(result.errors) >= 3

    def test_validate_unknown_conference_warns(self):
        """Test unknown conference generates warning."""
        data = {
            "nba_team_id": "123",
            "name": "Test Team",
            "abbreviation": "TST",
            "conference": "Unknown Conference",
        }
        result = TeamValidator.validate(data)

        assert result.is_valid
        assert any("conference" in w.lower() for w in result.warnings)
