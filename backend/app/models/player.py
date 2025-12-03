"""
NBA Player model.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class InjuryStatus(str, enum.Enum):
    HEALTHY = "healthy"
    QUESTIONABLE = "questionable"
    DOUBTFUL = "doubtful"
    OUT = "out"
    DAY_TO_DAY = "day_to_day"


class Player(Base):
    """NBA Player model."""

    __tablename__ = "players"

    id = Column(Integer, primary_key=True)  # NBA API player ID
    full_name = Column(String(255), nullable=False, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    position = Column(String(20))  # PG, SG, SF, PF, C
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    team_abbreviation = Column(String(10), index=True)

    # Player info
    jersey_number = Column(String(10))
    height = Column(String(10))  # e.g., "6-6"
    weight = Column(String(10))  # e.g., "220"
    birth_date = Column(Date)
    country = Column(String(100))

    # Draft info
    draft_year = Column(Integer)
    draft_round = Column(Integer)
    draft_number = Column(Integer)

    # Status
    is_active = Column(Boolean, default=True)
    injury_status = Column(Enum(InjuryStatus), default=InjuryStatus.HEALTHY)
    injury_detail = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    team = relationship("Team", back_populates="players")
    game_stats = relationship("PlayerGameStats", back_populates="player")
    predictions = relationship("PlayerPrediction", back_populates="player")

    def __repr__(self):
        return f"<Player {self.full_name}>"
