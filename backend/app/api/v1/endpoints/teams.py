"""
Team endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.team import Team
from app.models.player import Player
from app.schemas.team import TeamResponse, TeamListResponse
from app.schemas.player import PlayerBase
from app.core.exceptions import NotFoundException

router = APIRouter()


@router.get("", response_model=TeamListResponse)
async def list_teams(
    conference: Optional[str] = Query(None, description="Filter by conference (East/West)"),
    db: Session = Depends(get_db),
) -> TeamListResponse:
    """List all NBA teams."""
    q = db.query(Team)

    if conference:
        q = q.filter(Team.conference.ilike(conference))

    teams = q.order_by(Team.full_name).all()

    return TeamListResponse(
        teams=[TeamResponse.model_validate(t) for t in teams],
        total=len(teams),
    )


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    db: Session = Depends(get_db),
) -> TeamResponse:
    """Get team details by ID."""
    team = db.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise NotFoundException(detail=f"Team with ID {team_id} not found")

    return TeamResponse.model_validate(team)


@router.get("/{team_id}/roster")
async def get_team_roster(
    team_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """Get team roster."""
    team = db.query(Team).filter(Team.id == team_id).first()

    if not team:
        raise NotFoundException(detail=f"Team with ID {team_id} not found")

    players = (
        db.query(Player)
        .filter(Player.team_id == team_id, Player.is_active == True)
        .order_by(Player.position, Player.full_name)
        .all()
    )

    return {
        "team": TeamResponse.model_validate(team),
        "roster": [PlayerBase.model_validate(p) for p in players],
        "total": len(players),
    }


@router.get("/abbreviation/{abbreviation}", response_model=TeamResponse)
async def get_team_by_abbreviation(
    abbreviation: str,
    db: Session = Depends(get_db),
) -> TeamResponse:
    """Get team by abbreviation (e.g., LAL, BOS)."""
    team = db.query(Team).filter(Team.abbreviation == abbreviation.upper()).first()

    if not team:
        raise NotFoundException(detail=f"Team '{abbreviation}' not found")

    return TeamResponse.model_validate(team)
