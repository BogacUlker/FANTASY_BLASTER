"""
Player schemas.
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel


class PlayerBase(BaseModel):
    """Base player schema."""

    id: int
    full_name: str
    position: Optional[str] = None
    team_abbreviation: Optional[str] = None

    class Config:
        from_attributes = True


class PlayerResponse(PlayerBase):
    """Full player response schema."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    jersey_number: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    birth_date: Optional[date] = None
    country: Optional[str] = None
    is_active: bool = True
    injury_status: str = "healthy"
    injury_detail: Optional[str] = None

    class Config:
        from_attributes = True


class PlayerListResponse(BaseModel):
    """Paginated player list response."""

    players: List[PlayerBase]
    total: int
    page: int
    per_page: int
    pages: int


class PlayerGameStatsBase(BaseModel):
    """Base game stats schema."""

    game_date: date
    opponent_team_id: Optional[int] = None
    is_home: Optional[bool] = None
    minutes_played: Optional[float] = None
    points: Optional[int] = None
    rebounds: Optional[int] = None
    assists: Optional[int] = None
    steals: Optional[int] = None
    blocks: Optional[int] = None
    turnovers: Optional[int] = None
    fg_pct: Optional[float] = None
    fg3m: Optional[int] = None
    ft_pct: Optional[float] = None


class PlayerStatsResponse(BaseModel):
    """Player stats response with game log."""

    player: PlayerResponse
    recent_games: List[PlayerGameStatsBase]
    season_averages: dict

    class Config:
        from_attributes = True


class PlayerSearchParams(BaseModel):
    """Player search parameters."""

    query: Optional[str] = None
    team: Optional[str] = None
    position: Optional[str] = None
    is_active: Optional[bool] = True
    page: int = 1
    per_page: int = 20
