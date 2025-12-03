"""
NBA API client for fetching data from NBA Stats API.

Uses the nba_api package for reliable access to NBA statistics.
"""
import logging
from datetime import date, datetime
from typing import Any
import time
from functools import wraps

from nba_api.stats.endpoints import (
    commonallplayers,
    commonplayerinfo,
    commonteamroster,
    leaguegamefinder,
    boxscoretraditionalv2,
    playergamelog,
    scoreboardv2,
    teamgamelog,
)
from nba_api.stats.static import teams as static_teams
from nba_api.stats.static import players as static_players

logger = logging.getLogger(__name__)

# Rate limiting settings
MIN_REQUEST_INTERVAL = 0.6  # seconds between requests
_last_request_time = 0


def rate_limited(func):
    """Decorator to enforce rate limiting on API calls."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        global _last_request_time
        elapsed = time.time() - _last_request_time
        if elapsed < MIN_REQUEST_INTERVAL:
            time.sleep(MIN_REQUEST_INTERVAL - elapsed)
        _last_request_time = time.time()
        return func(*args, **kwargs)
    return wrapper


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry failed API calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"API call failed (attempt {attempt + 1}/{max_retries}): {e}"
                    )
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))
            raise last_error
        return wrapper
    return decorator


class NBAApiClient:
    """
    Client for fetching data from NBA Stats API.

    Handles rate limiting, retries, and data transformation.
    """

    # Current NBA season
    CURRENT_SEASON = "2024-25"

    # Season type codes
    SEASON_TYPE_REGULAR = "Regular Season"
    SEASON_TYPE_PLAYOFFS = "Playoffs"
    SEASON_TYPE_PRESEASON = "Pre Season"

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def get_all_teams() -> list[dict[str, Any]]:
        """
        Get all NBA teams from static data.

        Returns:
            List of team dictionaries with id, name, abbreviation, etc.
        """
        return static_teams.get_teams()

    @staticmethod
    def get_team_by_abbreviation(abbreviation: str) -> dict[str, Any] | None:
        """Get team by abbreviation (e.g., 'LAL', 'BOS')."""
        teams = static_teams.find_teams_by_abbreviation(abbreviation)
        return teams[0] if teams else None

    @staticmethod
    def get_all_players_static() -> list[dict[str, Any]]:
        """Get all players from static data (may not be current)."""
        return static_players.get_players()

    @rate_limited
    @retry_on_failure(max_retries=3)
    def get_all_active_players(self, season: str | None = None) -> list[dict[str, Any]]:
        """
        Get all active players for a season.

        Args:
            season: Season string (e.g., "2024-25"). Defaults to current.

        Returns:
            List of player dictionaries.
        """
        season = season or self.CURRENT_SEASON
        self.logger.info(f"Fetching all active players for season {season}")

        response = commonallplayers.CommonAllPlayers(
            is_only_current_season=1,
            season=season
        )

        players = response.get_normalized_dict()["CommonAllPlayers"]
        self.logger.info(f"Found {len(players)} active players")
        return players

    @rate_limited
    @retry_on_failure(max_retries=3)
    def get_player_info(self, player_id: int) -> dict[str, Any]:
        """
        Get detailed player information.

        Args:
            player_id: NBA player ID.

        Returns:
            Player info dictionary.
        """
        self.logger.debug(f"Fetching player info for ID {player_id}")

        response = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
        data = response.get_normalized_dict()

        return data["CommonPlayerInfo"][0] if data["CommonPlayerInfo"] else {}

    @rate_limited
    @retry_on_failure(max_retries=3)
    def get_team_roster(self, team_id: int, season: str | None = None) -> list[dict[str, Any]]:
        """
        Get team roster for a season.

        Args:
            team_id: NBA team ID.
            season: Season string. Defaults to current.

        Returns:
            List of player dictionaries on the roster.
        """
        season = season or self.CURRENT_SEASON
        self.logger.debug(f"Fetching roster for team {team_id}, season {season}")

        response = commonteamroster.CommonTeamRoster(
            team_id=team_id,
            season=season
        )

        return response.get_normalized_dict()["CommonTeamRoster"]

    @rate_limited
    @retry_on_failure(max_retries=3)
    def get_scoreboard(self, game_date: date) -> dict[str, Any]:
        """
        Get scoreboard for a specific date.

        Args:
            game_date: Date to fetch games for.

        Returns:
            Scoreboard data with games and line scores.
        """
        date_str = game_date.strftime("%Y-%m-%d")
        self.logger.info(f"Fetching scoreboard for {date_str}")

        response = scoreboardv2.ScoreboardV2(game_date=date_str)
        data = response.get_normalized_dict()

        return {
            "game_header": data.get("GameHeader", []),
            "line_score": data.get("LineScore", []),
            "series_standings": data.get("SeriesStandings", []),
        }

    @rate_limited
    @retry_on_failure(max_retries=3)
    def get_boxscore(self, game_id: str) -> dict[str, Any]:
        """
        Get traditional box score for a game.

        Args:
            game_id: NBA game ID (e.g., "0022400001").

        Returns:
            Box score data with player and team stats.
        """
        self.logger.debug(f"Fetching box score for game {game_id}")

        response = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
        data = response.get_normalized_dict()

        return {
            "player_stats": data.get("PlayerStats", []),
            "team_stats": data.get("TeamStats", []),
        }

    @rate_limited
    @retry_on_failure(max_retries=3)
    def get_player_game_log(
        self,
        player_id: int,
        season: str | None = None,
        season_type: str = "Regular Season"
    ) -> list[dict[str, Any]]:
        """
        Get game log for a player.

        Args:
            player_id: NBA player ID.
            season: Season string. Defaults to current.
            season_type: "Regular Season", "Playoffs", or "Pre Season".

        Returns:
            List of game log entries.
        """
        season = season or self.CURRENT_SEASON
        self.logger.debug(f"Fetching game log for player {player_id}, season {season}")

        response = playergamelog.PlayerGameLog(
            player_id=player_id,
            season=season,
            season_type_all_star=season_type
        )

        return response.get_normalized_dict()["PlayerGameLog"]

    @rate_limited
    @retry_on_failure(max_retries=3)
    def get_team_game_log(
        self,
        team_id: int,
        season: str | None = None,
        season_type: str = "Regular Season"
    ) -> list[dict[str, Any]]:
        """
        Get game log for a team.

        Args:
            team_id: NBA team ID.
            season: Season string. Defaults to current.
            season_type: "Regular Season", "Playoffs", or "Pre Season".

        Returns:
            List of game log entries.
        """
        season = season or self.CURRENT_SEASON
        self.logger.debug(f"Fetching game log for team {team_id}, season {season}")

        response = teamgamelog.TeamGameLog(
            team_id=team_id,
            season=season,
            season_type_all_star=season_type
        )

        return response.get_normalized_dict()["TeamGameLog"]

    @rate_limited
    @retry_on_failure(max_retries=3)
    def find_games_by_date_range(
        self,
        date_from: date,
        date_to: date,
        team_id: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Find games within a date range.

        Args:
            date_from: Start date.
            date_to: End date.
            team_id: Optional team filter.

        Returns:
            List of game dictionaries.
        """
        self.logger.info(f"Finding games from {date_from} to {date_to}")

        params = {
            "date_from_nullable": date_from.strftime("%m/%d/%Y"),
            "date_to_nullable": date_to.strftime("%m/%d/%Y"),
            "league_id_nullable": "00",  # NBA
        }

        if team_id:
            params["team_id_nullable"] = team_id

        response = leaguegamefinder.LeagueGameFinder(**params)

        return response.get_normalized_dict()["LeagueGameFinderResults"]

    def get_seasons_list(self, start_year: int = 2022, end_year: int | None = None) -> list[str]:
        """
        Generate list of season strings.

        Args:
            start_year: Starting year (e.g., 2022 for 2022-23 season).
            end_year: Ending year. Defaults to current.

        Returns:
            List of season strings (e.g., ["2022-23", "2023-24", "2024-25"]).
        """
        if end_year is None:
            end_year = datetime.now().year

        seasons = []
        for year in range(start_year, end_year + 1):
            season = f"{year}-{str(year + 1)[-2:]}"
            seasons.append(season)

        return seasons
