"""
Prediction schemas.
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from uuid import UUID


class CategoryPrediction(BaseModel):
    """Prediction for a single category."""

    value: float
    low: float
    high: float
    z_score: Optional[float] = None


class PredictionResponse(BaseModel):
    """Player prediction response."""

    id: UUID
    player_id: int
    player_name: str
    game_date: date
    opponent: Optional[str] = None
    is_home: Optional[bool] = None

    # Category predictions
    predictions: Dict[str, CategoryPrediction]

    # Aggregated metrics
    total_z_score: Optional[float] = None
    fantasy_points_projected: Optional[float] = None
    confidence: float

    # Explainability
    factors: Optional[List[Dict[str, Any]]] = None

    # Model info
    model_version: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionListResponse(BaseModel):
    """List of predictions response."""

    predictions: List[PredictionResponse]
    date: date
    total: int


class DailyPredictionsRequest(BaseModel):
    """Request for daily predictions."""

    date: Optional[date] = None
    player_ids: Optional[List[int]] = None
    min_confidence: Optional[float] = None
    categories: Optional[List[str]] = None
