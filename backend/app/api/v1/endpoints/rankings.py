"""
Rankings endpoints.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.player import Player
from app.models.game_stats import PlayerGameStats
from app.schemas.player import PlayerBase
from app.api.v1.dependencies import get_optional_user
from app.models.user import User

router = APIRouter()


@router.get("")
async def get_rankings(
    category: str = Query("points", description="Stat category to rank by"),
    time_period: str = Query("season", description="Time period: season, last_30, last_7"),
    position: Optional[str] = Query(None, description="Filter by position"),
    limit: int = Query(50, ge=1, le=200, description="Number of players"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
) -> dict:
    """Get player rankings by category."""
    # Get all active players with their stats
    players_with_stats = []

    # Get active players
    q = db.query(Player).filter(Player.is_active == True)

    if position:
        q = q.filter(Player.position.ilike(f"%{position}%"))

    players = q.all()

    for player in players:
        # Get stats for time period
        stats_query = db.query(PlayerGameStats).filter(
            PlayerGameStats.player_id == player.id
        )

        # Apply time period filter
        # Note: In production, you'd filter by actual dates
        stats = stats_query.all()

        if not stats:
            continue

        # Calculate average for category
        total_games = len(stats)

        category_map = {
            "points": lambda s: s.points or 0,
            "rebounds": lambda s: s.rebounds or 0,
            "assists": lambda s: s.assists or 0,
            "steals": lambda s: s.steals or 0,
            "blocks": lambda s: s.blocks or 0,
            "fg3m": lambda s: s.fg3m or 0,
            "turnovers": lambda s: s.turnovers or 0,
            "minutes": lambda s: float(s.minutes_played or 0),
        }

        if category not in category_map:
            category = "points"

        getter = category_map[category]
        total = sum(getter(s) for s in stats)
        average = total / total_games if total_games > 0 else 0

        players_with_stats.append({
            "player": PlayerBase.model_validate(player),
            "average": round(average, 2),
            "total": round(total, 2),
            "games_played": total_games,
        })

    # Sort by average
    players_with_stats.sort(key=lambda x: x["average"], reverse=True)

    # Add rank
    for i, p in enumerate(players_with_stats[:limit], 1):
        p["rank"] = i

    return {
        "category": category,
        "time_period": time_period,
        "rankings": players_with_stats[:limit],
        "total": len(players_with_stats),
    }


@router.get("/categories")
async def get_available_categories() -> dict:
    """Get list of available ranking categories."""
    return {
        "categories": [
            {"id": "points", "name": "Points", "description": "Points per game"},
            {"id": "rebounds", "name": "Rebounds", "description": "Rebounds per game"},
            {"id": "assists", "name": "Assists", "description": "Assists per game"},
            {"id": "steals", "name": "Steals", "description": "Steals per game"},
            {"id": "blocks", "name": "Blocks", "description": "Blocks per game"},
            {"id": "fg3m", "name": "3-Pointers Made", "description": "3-pointers made per game"},
            {"id": "turnovers", "name": "Turnovers", "description": "Turnovers per game (lower is better)"},
            {"id": "minutes", "name": "Minutes", "description": "Minutes per game"},
        ],
        "time_periods": [
            {"id": "season", "name": "Season", "description": "Full season stats"},
            {"id": "last_30", "name": "Last 30 Days", "description": "Last 30 days"},
            {"id": "last_7", "name": "Last 7 Days", "description": "Last 7 days"},
        ],
    }
