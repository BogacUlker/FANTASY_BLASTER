"""
Model training pipeline.

Handles end-to-end model training, evaluation, and registration.
"""
import logging
from datetime import date, timedelta
from typing import Any
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.ml.models.ensemble import EnsemblePredictor
from app.ml.models.predictor import StatPredictor
from app.ml.training.data_loader import TrainingDataLoader
from app.ml.serving.model_registry import ModelRegistry

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    End-to-end model training pipeline.

    Handles data loading, training, evaluation, and model registration.
    """

    # Default training configuration
    DEFAULT_CONFIG = {
        "lookback_days": 365,
        "validation_days": 30,
        "min_games": 10,
        "optimize_weights": True,
        "cross_validate": True,
        "n_cv_folds": 5,
    }

    def __init__(
        self,
        db: Session,
        model_dir: str = "models",
        config: dict[str, Any] | None = None
    ):
        """
        Initialize trainer.

        Args:
            db: Database session.
            model_dir: Directory for model storage.
            config: Training configuration override.
        """
        self.db = db
        self.model_dir = Path(model_dir)
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}

        self.data_loader = TrainingDataLoader(db)
        self.model_registry = ModelRegistry(str(self.model_dir))
        self.logger = logging.getLogger(__name__)

    def train_model(
        self,
        stat_type: str = "fantasy_points",
        end_date: date | None = None,
        model_type: str = "ensemble"
    ) -> dict[str, Any]:
        """
        Train a model for a specific stat type.

        Args:
            stat_type: Stat to predict.
            end_date: End date for training data (defaults to yesterday).
            model_type: "ensemble" or "xgboost".

        Returns:
            Training results dictionary.
        """
        end_date = end_date or (date.today() - timedelta(days=1))
        start_date = end_date - timedelta(days=self.config["lookback_days"])
        val_start = end_date - timedelta(days=self.config["validation_days"])

        self.logger.info(f"Training {stat_type} model: {start_date} to {end_date}")

        # Load training data
        X_train, y_train = self.data_loader.load_training_data(
            start_date=start_date,
            end_date=val_start,
            stat_type=stat_type,
            min_games=self.config["min_games"]
        )

        if len(X_train) < 100:
            raise ValueError(f"Insufficient training data: {len(X_train)} samples")

        self.logger.info(f"Training data: {len(X_train)} samples, {len(X_train.columns)} features")

        # Load validation data
        X_val, y_val = self.data_loader.load_training_data(
            start_date=val_start,
            end_date=end_date,
            stat_type=stat_type,
            min_games=1  # Lower threshold for validation
        )

        self.logger.info(f"Validation data: {len(X_val)} samples")

        # Align features between train and validation
        common_features = list(set(X_train.columns) & set(X_val.columns))
        X_train = X_train[common_features]
        X_val = X_val[common_features]

        # Train model
        if model_type == "ensemble":
            model = EnsemblePredictor(stat_type=stat_type)
        else:
            model = StatPredictor(stat_type=stat_type)

        model.fit(X_train, y_train, optimize_weights=self.config["optimize_weights"])

        # Evaluate on validation set
        metrics = self._evaluate_model(model, X_val, y_val)

        # Cross-validation (optional)
        cv_metrics = {}
        if self.config["cross_validate"]:
            cv_metrics = self._cross_validate(
                model, X_train, y_train, n_splits=self.config["n_cv_folds"]
            )
            metrics.update(cv_metrics)

        # Register model
        model_id = self.model_registry.register_model(
            model=model,
            model_name=f"{stat_type}_{model_type}",
            tags=[stat_type, model_type, "production"]
        )

        # Set as active model
        self.model_registry.set_active_model(model_id)

        self.logger.info(f"Model registered: {model_id}")

        return {
            "model_id": model_id,
            "stat_type": stat_type,
            "training_samples": len(X_train),
            "validation_samples": len(X_val),
            "features": len(common_features),
            "metrics": metrics,
            "training_period": f"{start_date} to {end_date}",
        }

    def train_all_models(self, end_date: date | None = None) -> list[dict[str, Any]]:
        """
        Train models for all stat types.

        Args:
            end_date: End date for training.

        Returns:
            List of training results.
        """
        stat_types = ["fantasy_points", "points", "rebounds", "assists"]
        results = []

        for stat_type in stat_types:
            try:
                result = self.train_model(stat_type, end_date)
                results.append(result)
                self.logger.info(f"✓ {stat_type} model trained successfully")
            except Exception as e:
                self.logger.error(f"✗ {stat_type} training failed: {e}")
                results.append({
                    "stat_type": stat_type,
                    "error": str(e)
                })

        return results

    def retrain_with_recent_data(
        self,
        stat_type: str = "fantasy_points",
        recent_days: int = 7
    ) -> dict[str, Any]:
        """
        Retrain model incrementally with recent data.

        Args:
            stat_type: Stat to retrain.
            recent_days: Days of new data to incorporate.

        Returns:
            Training results.
        """
        end_date = date.today() - timedelta(days=1)

        return self.train_model(
            stat_type=stat_type,
            end_date=end_date,
            model_type="ensemble"
        )

    def evaluate_model_on_date(
        self,
        model_id: str,
        evaluation_date: date
    ) -> dict[str, Any]:
        """
        Evaluate a model on a specific date's games.

        Args:
            model_id: Model to evaluate.
            evaluation_date: Date to evaluate on.

        Returns:
            Evaluation metrics.
        """
        model = self.model_registry.load_model(model_id.split("_")[0])

        if model is None:
            return {"error": f"Model {model_id} not found"}

        X, y, player_ids = self.data_loader.load_validation_data(
            evaluation_date, model.stat_type
        )

        if len(X) == 0:
            return {"error": "No games on evaluation date"}

        metrics = self._evaluate_model(model, X, y)

        # Add per-player breakdown
        predictions = model.predict(X)
        player_results = []

        for i, player_id in enumerate(player_ids):
            player_results.append({
                "player_id": player_id,
                "actual": float(y.iloc[i]),
                "predicted": float(predictions[i]),
                "error": float(abs(predictions[i] - y.iloc[i]))
            })

        return {
            "evaluation_date": evaluation_date.isoformat(),
            "samples": len(X),
            "metrics": metrics,
            "player_results": sorted(player_results, key=lambda x: x["error"])
        }

    def get_feature_importance_report(
        self,
        stat_type: str = "fantasy_points",
        top_n: int = 20
    ) -> dict[str, Any]:
        """
        Get feature importance report for a model.

        Args:
            stat_type: Stat type to analyze.
            top_n: Number of top features to return.

        Returns:
            Feature importance report.
        """
        model_id = self.model_registry.get_active_model(stat_type)

        if not model_id:
            return {"error": f"No active model for {stat_type}"}

        model = self.model_registry.load_model(stat_type)

        if model is None:
            return {"error": "Failed to load model"}

        importance = model.get_feature_importance()

        # Sort by importance
        sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)

        return {
            "stat_type": stat_type,
            "model_id": model_id,
            "total_features": len(importance),
            "top_features": [
                {"feature": f, "importance": round(i, 4)}
                for f, i in sorted_importance[:top_n]
            ],
            "importance_sum": round(sum(importance.values()), 4)
        }

    def _evaluate_model(
        self,
        model: EnsemblePredictor | StatPredictor,
        X: pd.DataFrame,
        y: pd.Series
    ) -> dict[str, float]:
        """Evaluate model on dataset."""
        predictions = model.predict(X)
        actuals = y.values

        # RMSE
        rmse = np.sqrt(np.mean((predictions - actuals) ** 2))

        # MAE
        mae = np.mean(np.abs(predictions - actuals))

        # R-squared
        ss_res = np.sum((actuals - predictions) ** 2)
        ss_tot = np.sum((actuals - np.mean(actuals)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # MAPE
        non_zero = actuals != 0
        if non_zero.sum() > 0:
            mape = np.mean(np.abs((actuals[non_zero] - predictions[non_zero]) / actuals[non_zero])) * 100
        else:
            mape = 0.0

        # Directional accuracy (predicting above/below average)
        mean_actual = np.mean(actuals)
        direction_correct = np.mean(
            (predictions > mean_actual) == (actuals > mean_actual)
        ) * 100

        return {
            "rmse": float(rmse),
            "mae": float(mae),
            "r2": float(r2),
            "mape": float(mape),
            "directional_accuracy": float(direction_correct),
        }

    def _cross_validate(
        self,
        model: EnsemblePredictor | StatPredictor,
        X: pd.DataFrame,
        y: pd.Series,
        n_splits: int = 5
    ) -> dict[str, float]:
        """Perform time-series cross-validation."""
        from sklearn.model_selection import TimeSeriesSplit

        tscv = TimeSeriesSplit(n_splits=n_splits)

        rmse_scores = []
        mae_scores = []

        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            # Train new model for this fold
            if isinstance(model, EnsemblePredictor):
                fold_model = EnsemblePredictor(stat_type=model.stat_type)
            else:
                fold_model = StatPredictor(stat_type=model.stat_type)

            fold_model.fit(X_train, y_train)

            predictions = fold_model.predict(X_test)
            actuals = y_test.values

            rmse_scores.append(np.sqrt(np.mean((predictions - actuals) ** 2)))
            mae_scores.append(np.mean(np.abs(predictions - actuals)))

        return {
            "cv_rmse_mean": float(np.mean(rmse_scores)),
            "cv_rmse_std": float(np.std(rmse_scores)),
            "cv_mae_mean": float(np.mean(mae_scores)),
            "cv_mae_std": float(np.std(mae_scores)),
        }


class TrainingScheduler:
    """
    Scheduler for automated model retraining.

    Handles periodic retraining and model refresh.
    """

    def __init__(self, db: Session, model_dir: str = "models"):
        self.trainer = ModelTrainer(db, model_dir)
        self.logger = logging.getLogger(__name__)

    def should_retrain(
        self,
        stat_type: str,
        max_age_days: int = 7
    ) -> bool:
        """
        Check if a model needs retraining.

        Args:
            stat_type: Stat type to check.
            max_age_days: Maximum model age before retraining.

        Returns:
            True if retraining is needed.
        """
        model_id = self.trainer.model_registry.get_active_model(stat_type)

        if not model_id:
            return True  # No model exists

        models = self.trainer.model_registry.list_models(stat_type=stat_type)

        if not models:
            return True

        latest = models[0]
        registered_at = latest.get("registered_at")

        if not registered_at:
            return True

        from datetime import datetime
        registration_date = datetime.fromisoformat(registered_at).date()
        age_days = (date.today() - registration_date).days

        return age_days > max_age_days

    def run_scheduled_training(self) -> list[dict[str, Any]]:
        """
        Run scheduled training for models that need it.

        Returns:
            Training results for models that were retrained.
        """
        stat_types = ["fantasy_points", "points", "rebounds", "assists"]
        results = []

        for stat_type in stat_types:
            if self.should_retrain(stat_type):
                self.logger.info(f"Retraining {stat_type} model...")
                try:
                    result = self.trainer.train_model(stat_type)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Retraining failed for {stat_type}: {e}")
                    results.append({"stat_type": stat_type, "error": str(e)})
            else:
                self.logger.info(f"{stat_type} model is up to date")

        return results
