"""
NBA Team model.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Team(Base):
    """NBA Team model."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)  # NBA API team ID
    full_name = Column(String(100), nullable=False)
    abbreviation = Column(String(10), nullable=False, index=True)
    nickname = Column(String(50))
    city = Column(String(50))
    state = Column(String(50))
    conference = Column(String(10))  # East, West
    division = Column(String(20))

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    players = relationship("Player", back_populates="team")

    def __repr__(self):
        return f"<Team {self.abbreviation}>"
