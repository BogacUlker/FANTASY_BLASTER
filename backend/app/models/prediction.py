"""
Player prediction model.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class PlayerPrediction(Base):
    """Player prediction model."""

    __tablename__ = "player_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    game_date = Column(Date, nullable=False, index=True)
    opponent_team_id = Column(Integer, ForeignKey("teams.id"))
    is_home = Column(Boolean)

    # Predictions stored as JSONB for flexibility
    # Format: {"points": {"value": 24.3, "low": 18, "high": 31}, ...}
    predictions = Column(JSONB, nullable=False)

    # Aggregated scores
    total_z_score = Column(Numeric(5, 2))
    fantasy_points_projected = Column(Numeric(6, 2))
    confidence = Column(Numeric(3, 2))  # 0.00 to 1.00

    # Model info
    model_name = Column(String(100))
    model_version = Column(String(50))

    # Factors affecting prediction (for explainability)
    factors = Column(JSONB)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    player = relationship("Player", back_populates="predictions")

    def __repr__(self):
        return f"<PlayerPrediction {self.player_id} - {self.game_date}>"
