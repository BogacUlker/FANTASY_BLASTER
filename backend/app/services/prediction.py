"""
Prediction service.
"""
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.prediction import PlayerPrediction
from app.models.player import Player
from app.core.cache import cached


class PredictionService:
    """Service for prediction-related operations."""

    def __init__(self, db: Session):
        self.db = db

    @cached(key_prefix="daily_predictions", ttl=300)
    def get_daily_predictions(
        self,
        prediction_date: date,
        category: str | None = None,
        min_confidence: float = 0.0,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[PlayerPrediction], int]:
        """Get predictions for a specific date."""
        query = self.db.query(PlayerPrediction).filter(
            PlayerPrediction.prediction_date == prediction_date
        )

        if min_confidence > 0:
            query = query.filter(PlayerPrediction.confidence >= min_confidence)

        total = query.count()
        predictions = (
            query.order_by(PlayerPrediction.confidence.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return predictions, total

    def get_player_predictions(
        self,
        player_id: int,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 10,
    ) -> list[PlayerPrediction]:
        """Get predictions for a specific player."""
        query = self.db.query(PlayerPrediction).filter(
            PlayerPrediction.player_id == player_id
        )

        if start_date:
            query = query.filter(PlayerPrediction.prediction_date >= start_date)
        if end_date:
            query = query.filter(PlayerPrediction.prediction_date <= end_date)

        return (
            query.order_by(PlayerPrediction.prediction_date.desc())
            .limit(limit)
            .all()
        )

    def get_prediction(
        self, player_id: int, prediction_date: date
    ) -> PlayerPrediction | None:
        """Get a specific prediction for player on a date."""
        return (
            self.db.query(PlayerPrediction)
            .filter(
                and_(
                    PlayerPrediction.player_id == player_id,
                    PlayerPrediction.prediction_date == prediction_date,
                )
            )
            .first()
        )

    @cached(key_prefix="top_predictions", ttl=600)
    def get_top_predictions(
        self,
        prediction_date: date,
        category: str = "points",
        limit: int = 10,
    ) -> list[dict]:
        """Get top predictions for a category on a date."""
        predictions = (
            self.db.query(PlayerPrediction)
            .join(Player)
            .filter(
                PlayerPrediction.prediction_date == prediction_date,
                Player.is_active == True,
            )
            .order_by(PlayerPrediction.confidence.desc())
            .limit(limit * 2)  # Get more to filter by category
            .all()
        )

        result = []
        for pred in predictions:
            if pred.predictions and category in pred.predictions:
                result.append(
                    {
                        "player_id": pred.player_id,
                        "player_name": pred.player.name if pred.player else None,
                        "team_id": pred.player.team_id if pred.player else None,
                        "category": category,
                        "predicted_value": pred.predictions.get(category),
                        "confidence": pred.confidence,
                        "factors": pred.factors,
                    }
                )
                if len(result) >= limit:
                    break

        return result

    def get_breakout_candidates(
        self,
        prediction_date: date,
        limit: int = 10,
    ) -> list[dict]:
        """Get players predicted to outperform their averages significantly."""
        predictions = (
            self.db.query(PlayerPrediction)
            .join(Player)
            .filter(
                PlayerPrediction.prediction_date == prediction_date,
                Player.is_active == True,
                PlayerPrediction.confidence >= 0.7,
            )
            .order_by(PlayerPrediction.confidence.desc())
            .limit(limit)
            .all()
        )

        # Filter for breakout candidates based on prediction factors
        breakouts = []
        for pred in predictions:
            factors = pred.factors or {}
            if factors.get("breakout_score", 0) >= 0.6:
                breakouts.append(
                    {
                        "player_id": pred.player_id,
                        "player_name": pred.player.name if pred.player else None,
                        "breakout_score": factors.get("breakout_score"),
                        "reasons": factors.get("breakout_reasons", []),
                        "predictions": pred.predictions,
                    }
                )

        return breakouts

    def create_prediction(
        self,
        player_id: int,
        prediction_date: date,
        predictions: dict,
        confidence: float,
        model_version: str,
        factors: dict | None = None,
    ) -> PlayerPrediction:
        """Create or update a prediction."""
        existing = self.get_prediction(player_id, prediction_date)

        if existing:
            existing.predictions = predictions
            existing.confidence = confidence
            existing.model_version = model_version
            existing.factors = factors
            self.db.commit()
            self.db.refresh(existing)
            return existing

        prediction = PlayerPrediction(
            player_id=player_id,
            prediction_date=prediction_date,
            predictions=predictions,
            confidence=confidence,
            model_version=model_version,
            factors=factors,
        )
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        return prediction
