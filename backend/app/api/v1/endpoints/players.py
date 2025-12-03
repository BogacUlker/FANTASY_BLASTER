"""
Player endpoints.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.player import Player
from app.models.game_stats import PlayerGameStats
from app.schemas.player import (
    PlayerResponse,
    PlayerListResponse,
    PlayerStatsResponse,
    PlayerBase,
)
from app.core.exceptions import NotFoundException
from app.core.cache import cached

router = APIRouter()


@router.get("", response_model=PlayerListResponse)
async def list_players(
    query: Optional[str] = Query(None, description="Search by name"),
    team: Optional[str] = Query(None, description="Filter by team abbreviation"),
    position: Optional[str] = Query(None, description="Filter by position"),
    is_active: bool = Query(True, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
) -> PlayerListResponse:
    """List players with filtering and pagination."""
    # Build query
    q = db.query(Player)

    if is_active is not None:
        q = q.filter(Player.is_active == is_active)

    if query:
        search = f"%{query}%"
        q = q.filter(
            or_(
                Player.full_name.ilike(search),
                Player.first_name.ilike(search),
                Player.last_name.ilike(search),
            )
        )

    if team:
        q = q.filter(Player.team_abbreviation == team.upper())

    if position:
        q = q.filter(Player.position.ilike(f"%{position}%"))

    # Get total count
    total = q.count()

    # Paginate
    offset = (page - 1) * per_page
    players = q.order_by(Player.full_name).offset(offset).limit(per_page).all()

    return PlayerListResponse(
        players=[PlayerBase.model_validate(p) for p in players],
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(
    player_id: int,
    db: Session = Depends(get_db),
) -> PlayerResponse:
    """Get player details by ID."""
    player = db.query(Player).filter(Player.id == player_id).first()

    if not player:
        raise NotFoundException(detail=f"Player with ID {player_id} not found")

    return PlayerResponse.model_validate(player)


@router.get("/{player_id}/stats", response_model=PlayerStatsResponse)
async def get_player_stats(
    player_id: int,
    games: int = Query(10, ge=1, le=82, description="Number of recent games"),
    db: Session = Depends(get_db),
) -> PlayerStatsResponse:
    """Get player statistics including recent games."""
    player = db.query(Player).filter(Player.id == player_id).first()

    if not player:
        raise NotFoundException(detail=f"Player with ID {player_id} not found")

    # Get recent games
    recent_games = (
        db.query(PlayerGameStats)
        .filter(PlayerGameStats.player_id == player_id)
        .order_by(PlayerGameStats.game_date.desc())
        .limit(games)
        .all()
    )

    # Calculate season averages
    all_games = (
        db.query(PlayerGameStats)
        .filter(PlayerGameStats.player_id == player_id)
        .all()
    )

    season_averages = {}
    if all_games:
        total_games = len(all_games)
        season_averages = {
            "games_played": total_games,
            "points": sum(g.points or 0 for g in all_games) / total_games,
            "rebounds": sum(g.rebounds or 0 for g in all_games) / total_games,
            "assists": sum(g.assists or 0 for g in all_games) / total_games,
            "steals": sum(g.steals or 0 for g in all_games) / total_games,
            "blocks": sum(g.blocks or 0 for g in all_games) / total_games,
            "turnovers": sum(g.turnovers or 0 for g in all_games) / total_games,
            "minutes": sum(float(g.minutes_played or 0) for g in all_games) / total_games,
        }

    return PlayerStatsResponse(
        player=PlayerResponse.model_validate(player),
        recent_games=[
            {
                "game_date": g.game_date,
                "opponent_team_id": g.opponent_team_id,
                "is_home": g.is_home,
                "minutes_played": float(g.minutes_played) if g.minutes_played else None,
                "points": g.points,
                "rebounds": g.rebounds,
                "assists": g.assists,
                "steals": g.steals,
                "blocks": g.blocks,
                "turnovers": g.turnovers,
                "fg_pct": float(g.fg_pct) if g.fg_pct else None,
                "fg3m": g.fg3m,
                "ft_pct": float(g.ft_pct) if g.ft_pct else None,
            }
            for g in recent_games
        ],
        season_averages=season_averages,
    )


@router.get("/search/autocomplete")
async def autocomplete_players(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=25, description="Max results"),
    db: Session = Depends(get_db),
) -> List[PlayerBase]:
    """Autocomplete player search."""
    search = f"%{q}%"

    players = (
        db.query(Player)
        .filter(
            Player.is_active == True,
            or_(
                Player.full_name.ilike(search),
                Player.first_name.ilike(search),
                Player.last_name.ilike(search),
            ),
        )
        .order_by(Player.full_name)
        .limit(limit)
        .all()
    )

    return [PlayerBase.model_validate(p) for p in players]
