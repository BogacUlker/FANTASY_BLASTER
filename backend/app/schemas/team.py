"""
Team schemas.
"""

from typing import Optional, List
from pydantic import BaseModel


class TeamBase(BaseModel):
    """Base team schema."""

    id: int
    full_name: str
    abbreviation: str


class TeamResponse(TeamBase):
    """Full team response schema."""

    nickname: Optional[str] = None
    city: Optional[str] = None
    conference: Optional[str] = None
    division: Optional[str] = None

    class Config:
        from_attributes = True


class TeamListResponse(BaseModel):
    """Team list response."""

    teams: List[TeamResponse]
    total: int
