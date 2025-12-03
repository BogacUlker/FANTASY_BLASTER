"""
Player service.
"""
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.player import Player
from app.models.game_stats import PlayerGameStats
from app.core.cache import cached


class PlayerService:
    """Service for player-related operations."""

    def __init__(self, db: Session):
        self.db = db

    @cached(key_prefix="players", ttl=300)
    def get_players(
        self,
        skip: int = 0,
        limit: int = 50,
        team_id: int | None = None,
        position: str | None = None,
        search: str | None = None,
        active_only: bool = True,
    ) -> tuple[list[Player], int]:
        """Get paginated list of players with filters."""
        query = self.db.query(Player)

        if active_only:
            query = query.filter(Player.is_active == True)
        if team_id:
            query = query.filter(Player.team_id == team_id)
        if position:
            query = query.filter(Player.position.ilike(f"%{position}%"))
        if search:
            query = query.filter(Player.name.ilike(f"%{search}%"))

        total = query.count()
        players = query.order_by(Player.name).offset(skip).limit(limit).all()

        return players, total

    def get_player(self, player_id: int) -> Player | None:
        """Get a single player by ID."""
        return self.db.query(Player).filter(Player.id == player_id).first()

    def get_player_by_nba_id(self, nba_player_id: str) -> Player | None:
        """Get a player by their NBA API ID."""
        return self.db.query(Player).filter(Player.nba_player_id == nba_player_id).first()

    def get_player_stats(
        self,
        player_id: int,
        last_n_games: int = 10,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[PlayerGameStats]:
        """Get player game stats with filters."""
        query = self.db.query(PlayerGameStats).filter(PlayerGameStats.player_id == player_id)

        if start_date:
            query = query.filter(PlayerGameStats.game_date >= start_date)
        if end_date:
            query = query.filter(PlayerGameStats.game_date <= end_date)

        query = query.order_by(PlayerGameStats.game_date.desc())

        if last_n_games:
            query = query.limit(last_n_games)

        return query.all()

    def get_player_averages(
        self,
        player_id: int,
        last_n_games: int = 10,
    ) -> dict:
        """Calculate player averages over last N games."""
        stats = self.get_player_stats(player_id, last_n_games=last_n_games)

        if not stats:
            return {}

        games_played = len(stats)
        totals = {
            "minutes": sum(s.minutes or 0 for s in stats),
            "points": sum(s.points or 0 for s in stats),
            "rebounds": sum(s.rebounds or 0 for s in stats),
            "assists": sum(s.assists or 0 for s in stats),
            "steals": sum(s.steals or 0 for s in stats),
            "blocks": sum(s.blocks or 0 for s in stats),
            "turnovers": sum(s.turnovers or 0 for s in stats),
            "fg_made": sum(s.field_goals_made or 0 for s in stats),
            "fg_attempted": sum(s.field_goals_attempted or 0 for s in stats),
            "three_made": sum(s.three_pointers_made or 0 for s in stats),
            "three_attempted": sum(s.three_pointers_attempted or 0 for s in stats),
            "ft_made": sum(s.free_throws_made or 0 for s in stats),
            "ft_attempted": sum(s.free_throws_attempted or 0 for s in stats),
        }

        return {
            "games_played": games_played,
            "minutes_avg": round(totals["minutes"] / games_played, 1),
            "points_avg": round(totals["points"] / games_played, 1),
            "rebounds_avg": round(totals["rebounds"] / games_played, 1),
            "assists_avg": round(totals["assists"] / games_played, 1),
            "steals_avg": round(totals["steals"] / games_played, 1),
            "blocks_avg": round(totals["blocks"] / games_played, 1),
            "turnovers_avg": round(totals["turnovers"] / games_played, 1),
            "fg_pct": round(totals["fg_made"] / totals["fg_attempted"] * 100, 1)
            if totals["fg_attempted"] > 0
            else 0,
            "three_pct": round(totals["three_made"] / totals["three_attempted"] * 100, 1)
            if totals["three_attempted"] > 0
            else 0,
            "ft_pct": round(totals["ft_made"] / totals["ft_attempted"] * 100, 1)
            if totals["ft_attempted"] > 0
            else 0,
        }

    def autocomplete_players(self, query: str, limit: int = 10) -> list[dict]:
        """Search players by name for autocomplete."""
        players = (
            self.db.query(Player)
            .filter(Player.is_active == True, Player.name.ilike(f"%{query}%"))
            .order_by(Player.name)
            .limit(limit)
            .all()
        )

        return [
            {
                "id": p.id,
                "name": p.name,
                "team_id": p.team_id,
                "position": p.position,
            }
            for p in players
        ]
