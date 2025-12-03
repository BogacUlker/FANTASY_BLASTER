"""
Data validation layer for NBA data.

Ensures data integrity and consistency before database operations.
"""
import logging
from datetime import date, datetime
from typing import Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a validation check."""
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    cleaned_data: dict[str, Any] | None = None


class PlayerValidator:
    """Validator for player data."""

    REQUIRED_FIELDS = ["nba_player_id", "name"]
    VALID_POSITIONS = ["G", "F", "C", "G-F", "F-G", "F-C", "C-F", "PG", "SG", "SF", "PF"]

    @classmethod
    def validate(cls, data: dict[str, Any]) -> ValidationResult:
        """
        Validate player data.

        Args:
            data: Raw player data dict.

        Returns:
            ValidationResult with cleaned data if valid.
        """
        errors = []
        warnings = []
        cleaned = {}

        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")

        if errors:
            return ValidationResult(False, errors, warnings)

        # Clean and validate NBA player ID
        nba_id = str(data.get("nba_player_id", "")).strip()
        if not nba_id.isdigit():
            errors.append(f"Invalid NBA player ID: {nba_id}")
        else:
            cleaned["nba_player_id"] = nba_id

        # Clean name
        name = str(data.get("name", "")).strip()
        if len(name) < 2:
            errors.append(f"Player name too short: {name}")
        elif len(name) > 255:
            warnings.append(f"Player name truncated: {name[:255]}...")
            cleaned["name"] = name[:255]
        else:
            cleaned["name"] = name

        # Validate position
        position = data.get("position")
        if position:
            position = str(position).upper().strip()
            if position not in cls.VALID_POSITIONS:
                warnings.append(f"Non-standard position: {position}")
            cleaned["position"] = position

        # Validate height (format: "6-9" or "6'9\"")
        height = data.get("height")
        if height:
            height = cls._normalize_height(str(height))
            if height:
                cleaned["height"] = height
            else:
                warnings.append(f"Could not parse height: {data.get('height')}")

        # Validate weight
        weight = data.get("weight")
        if weight is not None:
            try:
                weight_int = int(str(weight).replace(" lbs", "").strip())
                if 100 <= weight_int <= 400:
                    cleaned["weight"] = weight_int
                else:
                    warnings.append(f"Unusual weight value: {weight_int}")
                    cleaned["weight"] = weight_int
            except (ValueError, TypeError):
                warnings.append(f"Could not parse weight: {weight}")

        # Validate birth date
        birth_date = data.get("birth_date")
        if birth_date:
            parsed_date = cls._parse_date(birth_date)
            if parsed_date:
                # Sanity check: player should be between 18-50 years old
                age = (date.today() - parsed_date).days / 365.25
                if 18 <= age <= 50:
                    cleaned["birth_date"] = parsed_date
                else:
                    warnings.append(f"Unusual player age: {age:.1f} years")
                    cleaned["birth_date"] = parsed_date
            else:
                warnings.append(f"Could not parse birth date: {birth_date}")

        # Validate team ID
        team_id = data.get("team_id")
        if team_id is not None:
            try:
                cleaned["team_id"] = int(team_id)
            except (ValueError, TypeError):
                warnings.append(f"Invalid team ID: {team_id}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            cleaned_data=cleaned if len(errors) == 0 else None,
        )

    @staticmethod
    def _normalize_height(height: str) -> str | None:
        """Normalize height to 'X-Y' format."""
        import re

        # Handle "6-9" format
        match = re.match(r"(\d+)-(\d+)", height)
        if match:
            return f"{match.group(1)}-{match.group(2)}"

        # Handle "6'9\"" format
        match = re.match(r"(\d+)'(\d+)\"?", height)
        if match:
            return f"{match.group(1)}-{match.group(2)}"

        # Handle "69" (inches)
        match = re.match(r"^(\d{2})$", height.strip())
        if match:
            inches = int(match.group(1))
            feet = inches // 12
            remaining = inches % 12
            return f"{feet}-{remaining}"

        return None

    @staticmethod
    def _parse_date(date_val: Any) -> date | None:
        """Parse various date formats."""
        if isinstance(date_val, date):
            return date_val
        if not date_val:
            return None

        date_str = str(date_val)

        formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%b %d, %Y",
            "%B %d, %Y",
            "%m/%d/%Y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str[:10] if "T" in date_str else date_str, fmt).date()
            except ValueError:
                continue

        return None


class GameStatsValidator:
    """Validator for game statistics data."""

    STAT_RANGES = {
        "minutes": (0, 60),
        "points": (0, 100),
        "rebounds": (0, 40),
        "assists": (0, 30),
        "steals": (0, 15),
        "blocks": (0, 15),
        "turnovers": (0, 20),
        "field_goals_made": (0, 40),
        "field_goals_attempted": (0, 50),
        "three_pointers_made": (0, 20),
        "three_pointers_attempted": (0, 30),
        "free_throws_made": (0, 30),
        "free_throws_attempted": (0, 35),
        "personal_fouls": (0, 6),
        "plus_minus": (-60, 60),
    }

    @classmethod
    def validate(cls, data: dict[str, Any]) -> ValidationResult:
        """
        Validate game stats data.

        Args:
            data: Raw game stats dict.

        Returns:
            ValidationResult with cleaned data if valid.
        """
        errors = []
        warnings = []
        cleaned = {}

        # Required fields
        if not data.get("player_id"):
            errors.append("Missing player_id")
        else:
            cleaned["player_id"] = int(data["player_id"])

        if not data.get("game_id"):
            errors.append("Missing game_id")
        else:
            cleaned["game_id"] = str(data["game_id"])

        if not data.get("game_date"):
            errors.append("Missing game_date")
        else:
            game_date = data["game_date"]
            if isinstance(game_date, date):
                cleaned["game_date"] = game_date
            else:
                try:
                    cleaned["game_date"] = datetime.strptime(str(game_date)[:10], "%Y-%m-%d").date()
                except ValueError:
                    errors.append(f"Invalid game_date: {game_date}")

        if errors:
            return ValidationResult(False, errors, warnings)

        # Validate stat ranges
        for stat_name, (min_val, max_val) in cls.STAT_RANGES.items():
            value = data.get(stat_name)
            if value is not None:
                try:
                    num_val = float(value)
                    if num_val < min_val or num_val > max_val:
                        warnings.append(
                            f"Unusual {stat_name} value: {num_val} (expected {min_val}-{max_val})"
                        )
                    cleaned[stat_name] = num_val if stat_name == "minutes" else int(num_val)
                except (ValueError, TypeError):
                    warnings.append(f"Could not parse {stat_name}: {value}")

        # Validate shot attempts vs makes
        cls._validate_shot_consistency(cleaned, warnings)

        # Calculate fantasy points if not provided
        if "fantasy_points" not in cleaned:
            cleaned["fantasy_points"] = cls._calculate_fantasy_points(cleaned)

        return ValidationResult(
            is_valid=True,
            errors=errors,
            warnings=warnings,
            cleaned_data=cleaned,
        )

    @classmethod
    def _validate_shot_consistency(cls, data: dict, warnings: list) -> None:
        """Check that makes don't exceed attempts."""
        checks = [
            ("field_goals_made", "field_goals_attempted", "FG"),
            ("three_pointers_made", "three_pointers_attempted", "3PT"),
            ("free_throws_made", "free_throws_attempted", "FT"),
        ]

        for made_key, attempted_key, label in checks:
            made = data.get(made_key, 0) or 0
            attempted = data.get(attempted_key, 0) or 0
            if made > attempted:
                warnings.append(f"{label} makes ({made}) > attempts ({attempted})")

        # Check rebounds consistency
        oreb = data.get("offensive_rebounds", 0) or 0
        dreb = data.get("defensive_rebounds", 0) or 0
        total_reb = data.get("rebounds", 0) or 0

        if oreb + dreb > 0 and total_reb > 0:
            if abs((oreb + dreb) - total_reb) > 1:
                warnings.append(
                    f"Rebound mismatch: OREB({oreb}) + DREB({dreb}) != REB({total_reb})"
                )

    @staticmethod
    def _calculate_fantasy_points(stats: dict) -> float:
        """Calculate fantasy points using standard scoring."""
        pts = stats.get("points", 0) or 0
        reb = stats.get("rebounds", 0) or 0
        ast = stats.get("assists", 0) or 0
        stl = stats.get("steals", 0) or 0
        blk = stats.get("blocks", 0) or 0
        tov = stats.get("turnovers", 0) or 0

        return round(pts + reb * 1.2 + ast * 1.5 + stl * 3 + blk * 3 - tov, 1)


class TeamValidator:
    """Validator for team data."""

    VALID_CONFERENCES = ["Eastern", "Western"]
    VALID_DIVISIONS = [
        "Atlantic", "Central", "Southeast",
        "Northwest", "Pacific", "Southwest",
    ]

    @classmethod
    def validate(cls, data: dict[str, Any]) -> ValidationResult:
        """Validate team data."""
        errors = []
        warnings = []
        cleaned = {}

        # Required fields
        nba_team_id = data.get("nba_team_id")
        if not nba_team_id:
            errors.append("Missing nba_team_id")
        else:
            cleaned["nba_team_id"] = str(nba_team_id)

        name = data.get("name")
        if not name:
            errors.append("Missing team name")
        else:
            cleaned["name"] = str(name).strip()

        abbreviation = data.get("abbreviation")
        if not abbreviation:
            errors.append("Missing abbreviation")
        else:
            abbr = str(abbreviation).upper().strip()
            if len(abbr) != 3:
                warnings.append(f"Unusual abbreviation length: {abbr}")
            cleaned["abbreviation"] = abbr

        if errors:
            return ValidationResult(False, errors, warnings)

        # Optional fields
        city = data.get("city")
        if city:
            cleaned["city"] = str(city).strip()

        conference = data.get("conference")
        if conference:
            conf = str(conference).strip()
            if conf not in cls.VALID_CONFERENCES:
                warnings.append(f"Unknown conference: {conf}")
            cleaned["conference"] = conf

        division = data.get("division")
        if division:
            div = str(division).strip()
            if div not in cls.VALID_DIVISIONS:
                warnings.append(f"Unknown division: {div}")
            cleaned["division"] = div

        return ValidationResult(
            is_valid=True,
            errors=errors,
            warnings=warnings,
            cleaned_data=cleaned,
        )


class DataQualityChecker:
    """Utility for checking data quality across the database."""

    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def run_quality_checks(self) -> dict[str, Any]:
        """Run all data quality checks."""
        from app.models.player import Player
        from app.models.team import Team
        from app.models.game_stats import PlayerGameStats

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {},
            "summary": {},
        }

        # Check for players without teams
        orphan_players = self.db.query(Player).filter(
            Player.team_id.is_(None),
            Player.is_active == True
        ).count()
        results["checks"]["orphan_players"] = {
            "count": orphan_players,
            "status": "warning" if orphan_players > 0 else "ok",
        }

        # Check for duplicate game stats
        from sqlalchemy import func
        duplicates = self.db.query(
            PlayerGameStats.player_id,
            PlayerGameStats.game_id,
            func.count().label("count")
        ).group_by(
            PlayerGameStats.player_id,
            PlayerGameStats.game_id
        ).having(func.count() > 1).all()

        results["checks"]["duplicate_game_stats"] = {
            "count": len(duplicates),
            "status": "error" if duplicates else "ok",
        }

        # Check for unusual stat values
        unusual_stats = self.db.query(PlayerGameStats).filter(
            (PlayerGameStats.points > 70) |
            (PlayerGameStats.rebounds > 30) |
            (PlayerGameStats.assists > 25)
        ).count()
        results["checks"]["unusual_stats"] = {
            "count": unusual_stats,
            "status": "warning" if unusual_stats > 0 else "ok",
        }

        # Summary
        error_count = sum(
            1 for c in results["checks"].values() if c["status"] == "error"
        )
        warning_count = sum(
            1 for c in results["checks"].values() if c["status"] == "warning"
        )

        results["summary"] = {
            "total_checks": len(results["checks"]),
            "errors": error_count,
            "warnings": warning_count,
            "overall_status": "error" if error_count else ("warning" if warning_count else "ok"),
        }

        return results
