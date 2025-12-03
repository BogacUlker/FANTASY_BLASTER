"""
Box score ingestion service.

Handles fetching and storing game statistics from NBA API.
"""
import logging
from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.team import Team
from app.models.game_stats import PlayerGameStats
from app.services.nba.client import NBAApiClient

logger = logging.getLogger(__name__)


class BoxScoreService:
    """
    Service for fetching and storing box score data.

    Handles game stats ingestion and historical backfill.
    """

    def __init__(self, db: Session, nba_client: NBAApiClient | None = None):
        self.db = db
        self.nba_client = nba_client or NBAApiClient()
        self.logger = logging.getLogger(__name__)

    def ingest_games_for_date(self, game_date: date) -> dict[str, int]:
        """
        Ingest all games for a specific date.

        Args:
            game_date: Date to fetch games for.

        Returns:
            Dict with counts of processed games and stats.
        """
        self.logger.info(f"Ingesting games for {game_date}")

        scoreboard = self.nba_client.get_scoreboard(game_date)
        games = scoreboard.get("game_header", [])

        games_processed = 0
        stats_created = 0
        stats_updated = 0
        errors = 0

        for game in games:
            game_id = game.get("GAME_ID")
            game_status = game.get("GAME_STATUS_ID")

            # Only process completed games (status 3)
            if game_status != 3:
                self.logger.debug(f"Skipping game {game_id} - not completed (status {game_status})")
                continue

            try:
                result = self.ingest_boxscore(game_id, game_date)
                stats_created += result.get("created", 0)
                stats_updated += result.get("updated", 0)
                games_processed += 1
            except Exception as e:
                self.logger.error(f"Failed to ingest game {game_id}: {e}")
                errors += 1

        self.logger.info(
            f"Date {game_date} complete: {games_processed} games, "
            f"{stats_created} stats created, {stats_updated} updated, {errors} errors"
        )

        return {
            "games_processed": games_processed,
            "stats_created": stats_created,
            "stats_updated": stats_updated,
            "errors": errors,
        }

    def ingest_boxscore(self, game_id: str, game_date: date) -> dict[str, int]:
        """
        Ingest box score for a single game.

        Args:
            game_id: NBA game ID.
            game_date: Date of the game.

        Returns:
            Dict with counts of created and updated stats.
        """
        self.logger.debug(f"Ingesting box score for game {game_id}")

        boxscore = self.nba_client.get_boxscore(game_id)
        player_stats = boxscore.get("player_stats", [])

        # Build lookups
        player_lookup = self._build_player_lookup()
        team_lookup = self._build_team_lookup()

        created = 0
        updated = 0

        for stat in player_stats:
            try:
                result = self._upsert_player_game_stat(
                    stat, game_id, game_date, player_lookup, team_lookup
                )
                if result == "created":
                    created += 1
                elif result == "updated":
                    updated += 1
            except Exception as e:
                self.logger.warning(f"Failed to process stat for player: {e}")

        self.db.commit()
        return {"created": created, "updated": updated}

    def _upsert_player_game_stat(
        self,
        stat: dict[str, Any],
        game_id: str,
        game_date: date,
        player_lookup: dict[str, int],
        team_lookup: dict[str, int],
    ) -> str:
        """
        Insert or update a player game stat.

        Returns:
            "created", "updated", or "skipped"
        """
        nba_player_id = str(stat.get("PLAYER_ID"))
        player_id = player_lookup.get(nba_player_id)

        if not player_id:
            # Player not in database yet
            return "skipped"

        # Check for existing stat
        existing = self.db.query(PlayerGameStats).filter(
            PlayerGameStats.player_id == player_id,
            PlayerGameStats.game_id == game_id,
        ).first()

        # Parse minutes
        minutes = self._parse_minutes(stat.get("MIN"))

        # Determine opponent
        team_nba_id = str(stat.get("TEAM_ID"))
        team_id = team_lookup.get(team_nba_id)

        stat_data = {
            "minutes": minutes,
            "points": stat.get("PTS"),
            "rebounds": stat.get("REB"),
            "assists": stat.get("AST"),
            "steals": stat.get("STL"),
            "blocks": stat.get("BLK"),
            "turnovers": stat.get("TO"),
            "field_goals_made": stat.get("FGM"),
            "field_goals_attempted": stat.get("FGA"),
            "three_pointers_made": stat.get("FG3M"),
            "three_pointers_attempted": stat.get("FG3A"),
            "free_throws_made": stat.get("FTM"),
            "free_throws_attempted": stat.get("FTA"),
            "offensive_rebounds": stat.get("OREB"),
            "defensive_rebounds": stat.get("DREB"),
            "personal_fouls": stat.get("PF"),
            "plus_minus": stat.get("PLUS_MINUS"),
        }

        # Calculate fantasy points
        stat_data["fantasy_points"] = self._calculate_fantasy_points(stat_data)

        if existing:
            # Update existing
            for key, value in stat_data.items():
                setattr(existing, key, value)
            return "updated"
        else:
            # Create new
            game_stat = PlayerGameStats(
                player_id=player_id,
                game_id=game_id,
                game_date=game_date,
                **stat_data,
            )
            self.db.add(game_stat)
            return "created"

    def backfill_player_history(
        self,
        player_id: int,
        seasons: list[str] | None = None
    ) -> dict[str, int]:
        """
        Backfill historical stats for a player.

        Args:
            player_id: Database player ID.
            seasons: List of seasons. Defaults to last 3.

        Returns:
            Dict with counts of stats added.
        """
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise ValueError(f"Player {player_id} not found")

        seasons = seasons or self.nba_client.get_seasons_list(start_year=2022)
        self.logger.info(f"Backfilling history for {player.name} across {len(seasons)} seasons")

        total_created = 0
        total_updated = 0

        for season in seasons:
            try:
                game_log = self.nba_client.get_player_game_log(
                    int(player.nba_player_id),
                    season=season
                )

                for game in game_log:
                    result = self._process_game_log_entry(player.id, game)
                    if result == "created":
                        total_created += 1
                    elif result == "updated":
                        total_updated += 1

                self.db.commit()

            except Exception as e:
                self.logger.error(f"Failed to backfill season {season}: {e}")

        self.logger.info(
            f"Backfill complete for {player.name}: {total_created} created, {total_updated} updated"
        )

        return {"created": total_created, "updated": total_updated}

    def backfill_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> dict[str, int]:
        """
        Backfill games for a date range.

        Args:
            start_date: Start of range.
            end_date: End of range.

        Returns:
            Aggregated counts.
        """
        self.logger.info(f"Backfilling games from {start_date} to {end_date}")

        total_games = 0
        total_created = 0
        total_updated = 0
        total_errors = 0

        current_date = start_date
        while current_date <= end_date:
            try:
                result = self.ingest_games_for_date(current_date)
                total_games += result["games_processed"]
                total_created += result["stats_created"]
                total_updated += result["stats_updated"]
                total_errors += result["errors"]
            except Exception as e:
                self.logger.error(f"Failed to process date {current_date}: {e}")
                total_errors += 1

            current_date += timedelta(days=1)

        return {
            "games_processed": total_games,
            "stats_created": total_created,
            "stats_updated": total_updated,
            "errors": total_errors,
        }

    def _process_game_log_entry(self, player_id: int, game: dict[str, Any]) -> str:
        """Process a single game log entry."""
        game_id = game.get("Game_ID")
        game_date = self._parse_game_date(game.get("GAME_DATE"))

        if not game_id or not game_date:
            return "skipped"

        existing = self.db.query(PlayerGameStats).filter(
            PlayerGameStats.player_id == player_id,
            PlayerGameStats.game_id == game_id,
        ).first()

        minutes = self._parse_minutes(game.get("MIN"))

        stat_data = {
            "minutes": minutes,
            "points": game.get("PTS"),
            "rebounds": game.get("REB"),
            "assists": game.get("AST"),
            "steals": game.get("STL"),
            "blocks": game.get("BLK"),
            "turnovers": game.get("TOV"),
            "field_goals_made": game.get("FGM"),
            "field_goals_attempted": game.get("FGA"),
            "three_pointers_made": game.get("FG3M"),
            "three_pointers_attempted": game.get("FG3A"),
            "free_throws_made": game.get("FTM"),
            "free_throws_attempted": game.get("FTA"),
            "offensive_rebounds": game.get("OREB"),
            "defensive_rebounds": game.get("DREB"),
            "plus_minus": game.get("PLUS_MINUS"),
        }

        stat_data["fantasy_points"] = self._calculate_fantasy_points(stat_data)

        if existing:
            for key, value in stat_data.items():
                setattr(existing, key, value)
            return "updated"
        else:
            game_stat = PlayerGameStats(
                player_id=player_id,
                game_id=game_id,
                game_date=game_date,
                **stat_data,
            )
            self.db.add(game_stat)
            return "created"

    def _build_player_lookup(self) -> dict[str, int]:
        """Build NBA player ID to database ID lookup."""
        players = self.db.query(Player.nba_player_id, Player.id).all()
        return {p.nba_player_id: p.id for p in players}

    def _build_team_lookup(self) -> dict[str, int]:
        """Build NBA team ID to database ID lookup."""
        teams = self.db.query(Team.nba_team_id, Team.id).all()
        return {t.nba_team_id: t.id for t in teams}

    @staticmethod
    def _parse_minutes(minutes_str: str | None) -> float | None:
        """Parse minutes string (MM:SS) to float."""
        if not minutes_str:
            return None
        try:
            if ":" in str(minutes_str):
                parts = str(minutes_str).split(":")
                return float(parts[0]) + float(parts[1]) / 60
            return float(minutes_str)
        except (ValueError, IndexError):
            return None

    @staticmethod
    def _parse_game_date(date_str: str | None) -> date | None:
        """Parse game date string."""
        if not date_str:
            return None
        try:
            # Handle various formats
            for fmt in ["%Y-%m-%d", "%b %d, %Y", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
                except ValueError:
                    continue
            return None
        except Exception:
            return None

    @staticmethod
    def _calculate_fantasy_points(stats: dict[str, Any]) -> float:
        """
        Calculate fantasy points using standard scoring.

        Scoring:
        - Points: 1 pt
        - Rebounds: 1.2 pts
        - Assists: 1.5 pts
        - Steals: 3 pts
        - Blocks: 3 pts
        - Turnovers: -1 pt
        """
        pts = stats.get("points") or 0
        reb = stats.get("rebounds") or 0
        ast = stats.get("assists") or 0
        stl = stats.get("steals") or 0
        blk = stats.get("blocks") or 0
        tov = stats.get("turnovers") or 0

        return round(
            pts * 1.0 +
            reb * 1.2 +
            ast * 1.5 +
            stl * 3.0 +
            blk * 3.0 +
            tov * -1.0,
            1
        )
