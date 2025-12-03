"""
Prediction endpoints.
"""

from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.prediction import PlayerPrediction
from app.models.player import Player
from app.schemas.prediction import PredictionResponse, PredictionListResponse
from app.core.exceptions import NotFoundException
from app.api.v1.dependencies import get_current_user, get_optional_user
from app.models.user import User

router = APIRouter()


@router.get("/daily", response_model=PredictionListResponse)
async def get_daily_predictions(
    prediction_date: Optional[date] = Query(None, description="Date for predictions (default: today)"),
    min_confidence: Optional[float] = Query(None, ge=0, le=1, description="Minimum confidence threshold"),
    limit: int = Query(50, ge=1, le=200, description="Max predictions to return"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
) -> PredictionListResponse:
    """Get daily predictions for all players."""
    if prediction_date is None:
        prediction_date = date.today()

    q = (
        db.query(PlayerPrediction)
        .join(Player)
        .filter(PlayerPrediction.game_date == prediction_date)
    )

    if min_confidence:
        q = q.filter(PlayerPrediction.confidence >= min_confidence)

    predictions = (
        q.order_by(PlayerPrediction.total_z_score.desc())
        .limit(limit)
        .all()
    )

    return PredictionListResponse(
        predictions=[
            PredictionResponse(
                id=p.id,
                player_id=p.player_id,
                player_name=p.player.full_name,
                game_date=p.game_date,
                opponent=None,  # TODO: Add opponent info
                is_home=p.is_home,
                predictions=p.predictions,
                total_z_score=float(p.total_z_score) if p.total_z_score else None,
                fantasy_points_projected=float(p.fantasy_points_projected) if p.fantasy_points_projected else None,
                confidence=float(p.confidence) if p.confidence else 0.0,
                factors=p.factors,
                model_version=p.model_version,
                created_at=p.created_at,
            )
            for p in predictions
        ],
        date=prediction_date,
        total=len(predictions),
    )


@router.get("/player/{player_id}", response_model=PredictionResponse)
async def get_player_prediction(
    player_id: int,
    prediction_date: Optional[date] = Query(None, description="Date for prediction (default: today)"),
    db: Session = Depends(get_db),
) -> PredictionResponse:
    """Get prediction for a specific player."""
    if prediction_date is None:
        prediction_date = date.today()

    prediction = (
        db.query(PlayerPrediction)
        .join(Player)
        .filter(
            PlayerPrediction.player_id == player_id,
            PlayerPrediction.game_date == prediction_date,
        )
        .first()
    )

    if not prediction:
        raise NotFoundException(
            detail=f"No prediction found for player {player_id} on {prediction_date}"
        )

    return PredictionResponse(
        id=prediction.id,
        player_id=prediction.player_id,
        player_name=prediction.player.full_name,
        game_date=prediction.game_date,
        opponent=None,
        is_home=prediction.is_home,
        predictions=prediction.predictions,
        total_z_score=float(prediction.total_z_score) if prediction.total_z_score else None,
        fantasy_points_projected=float(prediction.fantasy_points_projected) if prediction.fantasy_points_projected else None,
        confidence=float(prediction.confidence) if prediction.confidence else 0.0,
        factors=prediction.factors,
        model_version=prediction.model_version,
        created_at=prediction.created_at,
    )


@router.get("/top", response_model=PredictionListResponse)
async def get_top_predictions(
    category: str = Query("total_z_score", description="Category to rank by"),
    prediction_date: Optional[date] = Query(None, description="Date for predictions"),
    limit: int = Query(20, ge=1, le=100, description="Number of top predictions"),
    db: Session = Depends(get_db),
) -> PredictionListResponse:
    """Get top predictions by category."""
    if prediction_date is None:
        prediction_date = date.today()

    q = (
        db.query(PlayerPrediction)
        .join(Player)
        .filter(PlayerPrediction.game_date == prediction_date)
    )

    # Order by specified category
    if category == "total_z_score":
        q = q.order_by(PlayerPrediction.total_z_score.desc())
    elif category == "fantasy_points":
        q = q.order_by(PlayerPrediction.fantasy_points_projected.desc())
    elif category == "confidence":
        q = q.order_by(PlayerPrediction.confidence.desc())
    else:
        q = q.order_by(PlayerPrediction.total_z_score.desc())

    predictions = q.limit(limit).all()

    return PredictionListResponse(
        predictions=[
            PredictionResponse(
                id=p.id,
                player_id=p.player_id,
                player_name=p.player.full_name,
                game_date=p.game_date,
                opponent=None,
                is_home=p.is_home,
                predictions=p.predictions,
                total_z_score=float(p.total_z_score) if p.total_z_score else None,
                fantasy_points_projected=float(p.fantasy_points_projected) if p.fantasy_points_projected else None,
                confidence=float(p.confidence) if p.confidence else 0.0,
                factors=p.factors,
                model_version=p.model_version,
                created_at=p.created_at,
            )
            for p in predictions
        ],
        date=prediction_date,
        total=len(predictions),
    )
