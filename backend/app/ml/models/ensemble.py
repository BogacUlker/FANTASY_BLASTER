"""
Ensemble predictor combining multiple models.

Uses XGBoost and LightGBM for robust predictions.
"""
import logging
import pickle
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xgboost as xgb
import lightgbm as lgb

from app.ml.models.base import BasePredictor, PredictionResult, ModelMetadata

logger = logging.getLogger(__name__)


class LightGBMPredictor(BasePredictor):
    """
    LightGBM-based predictor for player statistics.

    Faster training than XGBoost, good for large datasets.
    """

    DEFAULT_PARAMS = {
        "n_estimators": 500,
        "max_depth": 6,
        "learning_rate": 0.05,
        "num_leaves": 31,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_samples": 20,
        "reg_alpha": 0.1,
        "reg_lambda": 1.0,
        "objective": "regression",
        "metric": "rmse",
        "verbosity": -1,
        "random_state": 42,
    }

    def __init__(
        self,
        stat_type: str = "fantasy_points",
        params: dict[str, Any] | None = None
    ):
        self.stat_type = stat_type
        self.params = {**self.DEFAULT_PARAMS, **(params or {})}
        self.model: lgb.LGBMRegressor | None = None
        self.feature_names: list[str] = []
        self.metadata: ModelMetadata | None = None
        self.logger = logging.getLogger(__name__)

    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        validation_split: float = 0.2,
        **kwargs
    ) -> "LightGBMPredictor":
        """Train the LightGBM model."""
        self.logger.info(f"Training LightGBM {self.stat_type} predictor")

        self.feature_names = list(X.columns)
        X_clean = self._prepare_features(X)
        y_clean = y.fillna(0).values

        # Split for validation
        split_idx = int(len(X_clean) * (1 - validation_split))
        X_train, X_val = X_clean[:split_idx], X_clean[split_idx:]
        y_train, y_val = y_clean[:split_idx], y_clean[split_idx:]

        # Train model
        self.model = lgb.LGBMRegressor(**self.params)
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(stopping_rounds=50)]
        )

        # Store metadata
        predictions = self.model.predict(X_val)
        rmse = np.sqrt(np.mean((predictions - y_val) ** 2))

        self.metadata = ModelMetadata(
            model_type="lightgbm",
            target=self.stat_type,
            version="1.0.0",
            training_date=date.today(),
            training_samples=len(X_train),
            feature_count=len(self.feature_names),
            metrics={"rmse": float(rmse)},
            hyperparameters=self.params
        )

        self.logger.info(f"LightGBM training complete. RMSE: {rmse:.3f}")

        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        if self.model is None:
            raise ValueError("Model not trained.")

        X_clean = self._prepare_features(X)
        return np.clip(self.model.predict(X_clean), 0, None)

    def predict_with_uncertainty(
        self,
        X: pd.DataFrame
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Make predictions with uncertainty."""
        predictions = self.predict(X)

        # Use prediction variance estimate
        std_estimate = predictions * 0.2
        lower = predictions - 1.645 * std_estimate
        upper = predictions + 1.645 * std_estimate

        return predictions, np.clip(lower, 0, None), upper

    def get_feature_importance(self) -> dict[str, float]:
        """Get feature importance."""
        if self.model is None:
            raise ValueError("Model not trained.")

        importance = self.model.feature_importances_
        return dict(zip(self.feature_names, importance))

    def save(self, path: str) -> None:
        """Save model."""
        if self.model is None:
            raise ValueError("No model to save.")

        save_dict = {
            "model": self.model,
            "feature_names": self.feature_names,
            "stat_type": self.stat_type,
            "params": self.params,
            "metadata": self.metadata.to_dict() if self.metadata else None
        }

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(save_dict, f)

    def load(self, path: str) -> "LightGBMPredictor":
        """Load model."""
        with open(path, "rb") as f:
            save_dict = pickle.load(f)

        self.model = save_dict["model"]
        self.feature_names = save_dict["feature_names"]
        self.stat_type = save_dict["stat_type"]
        self.params = save_dict["params"]

        return self

    def _prepare_features(self, X: pd.DataFrame) -> np.ndarray:
        """Prepare features for prediction."""
        if self.feature_names:
            X = X.reindex(columns=self.feature_names, fill_value=0)

        for col in X.columns:
            if X[col].dtype == bool:
                X[col] = X[col].astype(int)

        return X.fillna(0).values.astype(np.float32)


class EnsemblePredictor:
    """
    Ensemble predictor combining XGBoost and LightGBM.

    Uses weighted averaging for more robust predictions.
    """

    # Default weights for ensemble
    DEFAULT_WEIGHTS = {
        "xgboost": 0.6,
        "lightgbm": 0.4,
    }

    def __init__(
        self,
        stat_type: str = "fantasy_points",
        weights: dict[str, float] | None = None
    ):
        """
        Initialize ensemble predictor.

        Args:
            stat_type: Stat to predict.
            weights: Model weights (must sum to 1.0).
        """
        self.stat_type = stat_type
        self.weights = weights or self.DEFAULT_WEIGHTS

        # Validate weights
        if abs(sum(self.weights.values()) - 1.0) > 0.01:
            raise ValueError("Weights must sum to 1.0")

        self.xgb_model: xgb.XGBRegressor | None = None
        self.lgb_model: lgb.LGBMRegressor | None = None
        self.feature_names: list[str] = []
        self.metadata: ModelMetadata | None = None
        self.logger = logging.getLogger(__name__)

    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        validation_split: float = 0.2,
        optimize_weights: bool = True,
        **kwargs
    ) -> "EnsemblePredictor":
        """
        Train all ensemble models.

        Args:
            X: Feature DataFrame.
            y: Target series.
            validation_split: Fraction for validation.
            optimize_weights: Whether to optimize weights on validation set.

        Returns:
            Self for chaining.
        """
        self.logger.info(f"Training ensemble for {self.stat_type}")

        self.feature_names = list(X.columns)
        X_clean = self._prepare_features(X)
        y_clean = y.fillna(0).values

        # Split data
        split_idx = int(len(X_clean) * (1 - validation_split))
        X_train, X_val = X_clean[:split_idx], X_clean[split_idx:]
        y_train, y_val = y_clean[:split_idx], y_clean[split_idx:]

        # Train XGBoost
        self.logger.info("Training XGBoost model...")
        xgb_params = {
            "n_estimators": 500,
            "max_depth": 6,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
            "early_stopping_rounds": 50,
        }
        self.xgb_model = xgb.XGBRegressor(**xgb_params)
        self.xgb_model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )

        # Train LightGBM
        self.logger.info("Training LightGBM model...")
        lgb_params = {
            "n_estimators": 500,
            "max_depth": 6,
            "learning_rate": 0.05,
            "num_leaves": 31,
            "random_state": 42,
            "verbosity": -1,
        }
        self.lgb_model = lgb.LGBMRegressor(**lgb_params)
        self.lgb_model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(stopping_rounds=50)]
        )

        # Optimize weights if requested
        if optimize_weights:
            self._optimize_weights(X_val, y_val)

        # Calculate ensemble metrics
        metrics = self._calculate_metrics(X_val, y_val)

        self.metadata = ModelMetadata(
            model_type="ensemble",
            target=self.stat_type,
            version="1.0.0",
            training_date=date.today(),
            training_samples=len(X_train),
            feature_count=len(self.feature_names),
            metrics=metrics,
            hyperparameters={"weights": self.weights}
        )

        self.logger.info(f"Ensemble training complete. RMSE: {metrics['rmse']:.3f}")

        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make ensemble predictions.

        Args:
            X: Feature DataFrame.

        Returns:
            Weighted average predictions.
        """
        if self.xgb_model is None or self.lgb_model is None:
            raise ValueError("Ensemble not trained.")

        X_clean = self._prepare_features(X)

        # Get individual predictions
        xgb_pred = self.xgb_model.predict(X_clean)
        lgb_pred = self.lgb_model.predict(X_clean)

        # Weighted average
        ensemble_pred = (
            self.weights["xgboost"] * xgb_pred +
            self.weights["lightgbm"] * lgb_pred
        )

        return np.clip(ensemble_pred, 0, None)

    def predict_with_uncertainty(
        self,
        X: pd.DataFrame
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Make predictions with uncertainty estimates.

        Uses disagreement between models as uncertainty measure.
        """
        X_clean = self._prepare_features(X)

        xgb_pred = self.xgb_model.predict(X_clean)
        lgb_pred = self.lgb_model.predict(X_clean)

        # Ensemble prediction
        ensemble_pred = (
            self.weights["xgboost"] * xgb_pred +
            self.weights["lightgbm"] * lgb_pred
        )

        # Use model disagreement as uncertainty
        model_std = np.abs(xgb_pred - lgb_pred) / 2

        # Also add inherent prediction uncertainty
        base_uncertainty = ensemble_pred * 0.15

        total_uncertainty = np.sqrt(model_std**2 + base_uncertainty**2)

        lower = ensemble_pred - 1.645 * total_uncertainty
        upper = ensemble_pred + 1.645 * total_uncertainty

        return ensemble_pred, np.clip(lower, 0, None), upper

    def predict_player(
        self,
        features: dict[str, Any],
        player_id: int,
        as_of_date: date | None = None
    ) -> PredictionResult:
        """
        Make prediction for a single player.

        Args:
            features: Feature dictionary.
            player_id: Player ID.
            as_of_date: Reference date.

        Returns:
            PredictionResult with ensemble prediction.
        """
        X = pd.DataFrame([features])
        pred, lower, upper = self.predict_with_uncertainty(X)

        # Calculate confidence
        interval_width = (upper[0] - lower[0]) / (pred[0] + 1e-6)
        confidence = max(0.0, min(1.0, 1.0 - interval_width / 2))

        # Get combined feature importance
        factors = self._get_ensemble_factors(X.iloc[0])

        return PredictionResult(
            player_id=player_id,
            stat_type=self.stat_type,
            prediction=float(pred[0]),
            lower_bound=float(lower[0]),
            upper_bound=float(upper[0]),
            confidence=confidence,
            factors=factors,
            as_of_date=as_of_date
        )

    def get_feature_importance(self) -> dict[str, float]:
        """Get ensemble feature importance (weighted average)."""
        if self.xgb_model is None or self.lgb_model is None:
            raise ValueError("Ensemble not trained.")

        xgb_importance = self.xgb_model.feature_importances_
        lgb_importance = self.lgb_model.feature_importances_

        ensemble_importance = (
            self.weights["xgboost"] * xgb_importance +
            self.weights["lightgbm"] * lgb_importance
        )

        return dict(zip(self.feature_names, ensemble_importance))

    def save(self, path: str) -> None:
        """Save ensemble to disk."""
        if self.xgb_model is None or self.lgb_model is None:
            raise ValueError("No models to save.")

        save_dict = {
            "xgb_model": self.xgb_model,
            "lgb_model": self.lgb_model,
            "weights": self.weights,
            "feature_names": self.feature_names,
            "stat_type": self.stat_type,
            "metadata": self.metadata.to_dict() if self.metadata else None
        }

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(save_dict, f)

        self.logger.info(f"Ensemble saved to {path}")

    def load(self, path: str) -> "EnsemblePredictor":
        """Load ensemble from disk."""
        with open(path, "rb") as f:
            save_dict = pickle.load(f)

        self.xgb_model = save_dict["xgb_model"]
        self.lgb_model = save_dict["lgb_model"]
        self.weights = save_dict["weights"]
        self.feature_names = save_dict["feature_names"]
        self.stat_type = save_dict["stat_type"]

        self.logger.info(f"Ensemble loaded from {path}")

        return self

    def _prepare_features(self, X: pd.DataFrame) -> np.ndarray:
        """Prepare features for prediction."""
        if self.feature_names:
            X = X.reindex(columns=self.feature_names, fill_value=0)

        for col in X.columns:
            if X[col].dtype == bool:
                X[col] = X[col].astype(int)

        return X.fillna(0).values.astype(np.float32)

    def _optimize_weights(
        self,
        X_val: np.ndarray,
        y_val: np.ndarray
    ) -> None:
        """Optimize weights on validation set."""
        xgb_pred = self.xgb_model.predict(X_val)
        lgb_pred = self.lgb_model.predict(X_val)

        best_rmse = float("inf")
        best_xgb_weight = 0.5

        # Grid search over weights
        for xgb_w in np.arange(0.3, 0.8, 0.05):
            lgb_w = 1.0 - xgb_w
            ensemble_pred = xgb_w * xgb_pred + lgb_w * lgb_pred
            rmse = np.sqrt(np.mean((ensemble_pred - y_val) ** 2))

            if rmse < best_rmse:
                best_rmse = rmse
                best_xgb_weight = xgb_w

        self.weights = {
            "xgboost": float(best_xgb_weight),
            "lightgbm": float(1.0 - best_xgb_weight)
        }

        self.logger.info(f"Optimized weights: XGB={best_xgb_weight:.2f}, LGB={1-best_xgb_weight:.2f}")

    def _calculate_metrics(
        self,
        X_val: np.ndarray,
        y_val: np.ndarray
    ) -> dict[str, float]:
        """Calculate ensemble metrics."""
        predictions = self.predict(pd.DataFrame(X_val, columns=self.feature_names))

        rmse = np.sqrt(np.mean((predictions - y_val) ** 2))
        mae = np.mean(np.abs(predictions - y_val))

        ss_res = np.sum((y_val - predictions) ** 2)
        ss_tot = np.sum((y_val - np.mean(y_val)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        return {
            "rmse": float(rmse),
            "mae": float(mae),
            "r2": float(r2),
        }

    def _get_ensemble_factors(self, features: pd.Series) -> dict[str, float]:
        """Get top contributing factors from ensemble."""
        importance = self.get_feature_importance()

        contributions = {}
        for name, imp in importance.items():
            value = features.get(name, 0)
            contrib = float(imp * abs(float(value) if value else 0))
            if contrib > 0.01:
                contributions[name] = round(contrib, 4)

        sorted_factors = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_factors[:5])
