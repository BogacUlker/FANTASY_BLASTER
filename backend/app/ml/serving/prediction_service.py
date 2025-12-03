"""
Prediction serving layer.

Handles model loading, caching, and prediction serving for the API.
"""
import logging
from datetime import date, datetime, timedelta
from typing import Any
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.prediction import Prediction
from app.ml.features.engineer import FeatureEngineer
from app.ml.features.player_features import PlayerFeatureBuilder
from app.ml.features.game_features import GameContextFeatureBuilder
from app.ml.models.ensemble import EnsemblePredictor
from app.ml.models.base import PredictionResult

logger = logging.getLogger(__name__)


class PredictionService:
    """
    Service for generating and serving predictions.

    Handles feature engineering, model inference, and result storage.
    """

    # Model paths
    MODEL_DIR = Path("models")

    # Cache TTL
    CACHE_TTL_HOURS = 4

    def __init__(self, db: Session, model_dir: str | None = None):
        """
        Initialize prediction service.

        Args:
            db: Database session.
            model_dir: Optional custom model directory.
        """
        self.db = db
        self.model_dir = Path(model_dir) if model_dir else self.MODEL_DIR
        self.logger = logging.getLogger(__name__)

        # Initialize feature builders
        self.feature_engineer = FeatureEngineer(db)
        self.player_feature_builder = PlayerFeatureBuilder(db)
        self.game_feature_builder = GameContextFeatureBuilder(db)

        # Model cache
        self._models: dict[str, EnsemblePredictor] = {}

    def predict_player_stats(
        self,
        player_id: int,
        game_date: date | None = None,
        stat_types: list[str] | None = None,
        force_refresh: bool = False
    ) -> list[PredictionResult]:
        """
        Generate predictions for a player.

        Args:
            player_id: Database player ID.
            game_date: Target game date (defaults to today).
            stat_types: Stats to predict (defaults to all).
            force_refresh: Skip cache and regenerate.

        Returns:
            List of PredictionResult objects.
        """
        game_date = game_date or date.today()
        stat_types = stat_types or ["fantasy_points", "points", "rebounds", "assists"]

        # Check cache first
        if not force_refresh:
            cached = self._get_cached_predictions(player_id, game_date, stat_types)
            if cached:
                return cached

        # Build features
        features = self._build_player_features(player_id, game_date)

        if not features:
            self.logger.warning(f"No features for player {player_id}")
            return []

        # Generate predictions for each stat type
        predictions = []
        for stat_type in stat_types:
            try:
                result = self._predict_stat(player_id, stat_type, features, game_date)
                if result:
                    predictions.append(result)
                    self._cache_prediction(result)
            except Exception as e:
                self.logger.error(f"Prediction failed for {stat_type}: {e}")

        return predictions

    def predict_batch(
        self,
        player_ids: list[int],
        game_date: date | None = None,
        stat_type: str = "fantasy_points"
    ) -> list[PredictionResult]:
        """
        Generate predictions for multiple players.

        Args:
            player_ids: List of player IDs.
            game_date: Target game date.
            stat_type: Stat to predict.

        Returns:
            List of predictions.
        """
        game_date = game_date or date.today()
        predictions = []

        # Build batch features
        batch_features = self.feature_engineer.build_batch_features(
            player_ids, game_date
        )

        model = self._get_model(stat_type)

        for player_id in player_ids:
            try:
                player_features = batch_features[
                    batch_features["player_id"] == player_id
                ]

                if player_features.empty:
                    continue

                # Drop metadata columns for prediction
                feature_cols = [c for c in player_features.columns
                               if c not in ["player_id", "as_of_date"]]
                X = player_features[feature_cols].iloc[0].to_dict()

                result = model.predict_player(X, player_id, game_date)
                predictions.append(result)
                self._cache_prediction(result)

            except Exception as e:
                self.logger.error(f"Batch prediction failed for player {player_id}: {e}")

        return predictions

    def get_top_predictions(
        self,
        game_date: date | None = None,
        stat_type: str = "fantasy_points",
        limit: int = 25,
        position: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get top predicted performers.

        Args:
            game_date: Target date.
            stat_type: Stat type to rank by.
            limit: Number of players to return.
            position: Optional position filter.

        Returns:
            List of player prediction dictionaries.
        """
        game_date = game_date or date.today()

        # Get active players
        query = self.db.query(Player).filter(Player.is_active == True)

        if position:
            query = query.filter(Player.position == position)

        players = query.limit(200).all()
        player_ids = [p.id for p in players]

        # Generate predictions
        predictions = self.predict_batch(player_ids, game_date, stat_type)

        # Sort by prediction value
        predictions.sort(key=lambda x: x.prediction, reverse=True)

        # Build response with player info
        results = []
        for pred in predictions[:limit]:
            player = self.db.query(Player).filter(Player.id == pred.player_id).first()
            if player:
                results.append({
                    "player_id": player.id,
                    "player_name": player.name,
                    "position": player.position,
                    "team_id": player.team_id,
                    "stat_type": pred.stat_type,
                    "prediction": pred.prediction,
                    "lower_bound": pred.lower_bound,
                    "upper_bound": pred.upper_bound,
                    "confidence": pred.confidence,
                    "factors": pred.factors,
                })

        return results

    def get_breakout_candidates(
        self,
        game_date: date | None = None,
        min_upside: float = 0.2,
        limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Identify players with high breakout potential.

        Args:
            game_date: Target date.
            min_upside: Minimum upside threshold (prediction/average - 1).
            limit: Number of candidates to return.

        Returns:
            List of breakout candidate dictionaries.
        """
        game_date = game_date or date.today()

        # Get predictions
        top_predictions = self.get_top_predictions(
            game_date, "fantasy_points", limit=100
        )

        breakouts = []
        for pred in top_predictions:
            player_id = pred["player_id"]

            # Get player's season average
            features = self._build_player_features(player_id, game_date)
            if not features:
                continue

            season_avg = features.get("fantasy_points_avg_30g", 0)
            if season_avg <= 0:
                continue

            # Calculate upside
            upside = (pred["prediction"] - season_avg) / season_avg

            if upside >= min_upside:
                breakouts.append({
                    **pred,
                    "season_avg": season_avg,
                    "upside_pct": round(upside * 100, 1),
                    "prediction_vs_avg": pred["prediction"] - season_avg,
                })

        # Sort by upside
        breakouts.sort(key=lambda x: x["upside_pct"], reverse=True)

        return breakouts[:limit]

    def _build_player_features(
        self,
        player_id: int,
        game_date: date
    ) -> dict[str, Any]:
        """Build complete feature set for a player."""
        # Get player
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {}

        features = {}

        # Core features
        try:
            core_features = self.feature_engineer.build_player_features(
                player_id, game_date
            )
            features.update(core_features)
        except Exception as e:
            self.logger.error(f"Core feature build failed: {e}")
            return {}

        # Player-specific features
        try:
            injury_features = self.player_feature_builder.build_injury_features(player)
            features.update(injury_features)

            role_features = self.player_feature_builder.build_role_features(
                player_id, game_date
            )
            features.update(role_features)

            rate_features = self.player_feature_builder.build_per_minute_features(
                player_id, game_date
            )
            features.update(rate_features)

            ceiling_features = self.player_feature_builder.build_ceiling_floor_features(
                player_id, game_date
            )
            features.update(ceiling_features)
        except Exception as e:
            self.logger.warning(f"Player feature build warning: {e}")

        # Game context features
        try:
            time_features = self.game_feature_builder.build_time_context_features(
                game_date
            )
            features.update(time_features)

            if player.team_id:
                schedule_features = self.game_feature_builder.build_schedule_density_features(
                    player.team_id, game_date
                )
                features.update(schedule_features)
        except Exception as e:
            self.logger.warning(f"Game feature build warning: {e}")

        return features

    def _predict_stat(
        self,
        player_id: int,
        stat_type: str,
        features: dict[str, Any],
        game_date: date
    ) -> PredictionResult | None:
        """Generate prediction for a specific stat."""
        model = self._get_model(stat_type)

        if model is None:
            # Fallback to simple average
            return self._simple_prediction(player_id, stat_type, features, game_date)

        return model.predict_player(features, player_id, game_date)

    def _simple_prediction(
        self,
        player_id: int,
        stat_type: str,
        features: dict[str, Any],
        game_date: date
    ) -> PredictionResult:
        """Simple prediction based on recent averages (fallback)."""
        avg_key = f"{stat_type}_avg_10g"
        prediction = features.get(avg_key, 0)

        std_key = f"{stat_type}_std"
        std = features.get(std_key, prediction * 0.2)

        return PredictionResult(
            player_id=player_id,
            stat_type=stat_type,
            prediction=prediction,
            lower_bound=max(0, prediction - 1.645 * std),
            upper_bound=prediction + 1.645 * std,
            confidence=0.5,  # Lower confidence for simple model
            factors={"recent_average": prediction},
            as_of_date=game_date
        )

    def _get_model(self, stat_type: str) -> EnsemblePredictor | None:
        """Get or load model for stat type."""
        if stat_type in self._models:
            return self._models[stat_type]

        model_path = self.model_dir / f"{stat_type}_ensemble.pkl"

        if model_path.exists():
            try:
                model = EnsemblePredictor(stat_type=stat_type)
                model.load(str(model_path))
                self._models[stat_type] = model
                return model
            except Exception as e:
                self.logger.error(f"Failed to load model {model_path}: {e}")

        return None

    def _get_cached_predictions(
        self,
        player_id: int,
        game_date: date,
        stat_types: list[str]
    ) -> list[PredictionResult] | None:
        """Check for cached predictions."""
        cutoff = datetime.utcnow() - timedelta(hours=self.CACHE_TTL_HOURS)

        cached = self.db.query(Prediction).filter(
            Prediction.player_id == player_id,
            Prediction.prediction_date == game_date,
            Prediction.created_at >= cutoff
        ).all()

        if not cached:
            return None

        # Check if all requested stat types are cached
        cached_types = {p.stat_type for p in cached if hasattr(p, 'stat_type')}
        if not set(stat_types).issubset(cached_types):
            return None

        results = []
        for pred in cached:
            if hasattr(pred, 'stat_type') and pred.stat_type in stat_types:
                results.append(PredictionResult(
                    player_id=pred.player_id,
                    stat_type=pred.stat_type,
                    prediction=pred.predicted_value,
                    lower_bound=pred.lower_bound,
                    upper_bound=pred.upper_bound,
                    confidence=pred.confidence,
                    factors=pred.factors or {},
                    as_of_date=game_date
                ))

        return results if results else None

    def _cache_prediction(self, result: PredictionResult) -> None:
        """Store prediction in database cache."""
        try:
            prediction = Prediction(
                player_id=result.player_id,
                prediction_date=result.as_of_date or date.today(),
                predicted_value=result.prediction,
                lower_bound=result.lower_bound,
                upper_bound=result.upper_bound,
                confidence=result.confidence,
                factors=result.factors,
            )
            self.db.add(prediction)
            self.db.commit()
        except Exception as e:
            self.logger.warning(f"Failed to cache prediction: {e}")
            self.db.rollback()
