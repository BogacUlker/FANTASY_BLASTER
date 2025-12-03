"""
Player game statistics model.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from app.database import Base


class PlayerGameStats(Base):
    """Player game statistics model."""

    __tablename__ = "player_game_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    game_id = Column(String(20), nullable=False, index=True)
    game_date = Column(Date, nullable=False, index=True)
    season = Column(String(10), nullable=False)
    opponent_team_id = Column(Integer, ForeignKey("teams.id"))
    is_home = Column(Boolean)

    # Minutes
    minutes_played = Column(Numeric(5, 2))

    # Scoring
    points = Column(Integer)
    fgm = Column(Integer)  # Field goals made
    fga = Column(Integer)  # Field goals attempted
    fg_pct = Column(Numeric(5, 3))
    fg3m = Column(Integer)  # 3-pointers made
    fg3a = Column(Integer)  # 3-pointers attempted
    fg3_pct = Column(Numeric(5, 3))
    ftm = Column(Integer)  # Free throws made
    fta = Column(Integer)  # Free throws attempted
    ft_pct = Column(Numeric(5, 3))

    # Rebounds
    offensive_rebounds = Column(Integer)
    defensive_rebounds = Column(Integer)
    rebounds = Column(Integer)

    # Other stats
    assists = Column(Integer)
    steals = Column(Integer)
    blocks = Column(Integer)
    turnovers = Column(Integer)
    personal_fouls = Column(Integer)
    plus_minus = Column(Integer)

    # Calculated fantasy points
    fantasy_points_standard = Column(Numeric(6, 2))

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    player = relationship("Player", back_populates="game_stats")

    # Unique constraint
    __table_args__ = (
        {"postgresql_partition_by": None},  # Can partition by season later
    )

    def __repr__(self):
        return f"<PlayerGameStats {self.player_id} - {self.game_date}>"
