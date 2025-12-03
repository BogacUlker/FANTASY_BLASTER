"""
XGBoost-based stat predictor.

Primary model for fantasy basketball stat predictions.
"""
import logging
import pickle
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import cross_val_score, TimeSeriesSplit

from app.ml.models.base import BasePredictor, PredictionResult, ModelMetadata

logger = logging.getLogger(__name__)


class StatPredictor(BasePredictor):
    """
    XGBoost-based predictor for player statistics.

    Uses gradient boosting for robust predictions with
    uncertainty estimation via quantile regression.
    """

    # Default hyperparameters
    DEFAULT_PARAMS = {
        "n_estimators": 500,
        "max_depth": 6,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 5,
        "gamma": 0.1,
        "reg_alpha": 0.1,
        "reg_lambda": 1.0,
        "objective": "reg:squarederror",
        "eval_metric": "rmse",
        "early_stopping_rounds": 50,
        "random_state": 42,
    }

    # Stat types supported
    STAT_TYPES = [
        "fantasy_points",
        "points",
        "rebounds",
        "assists",
        "steals",
        "blocks",
        "minutes",
    ]

    def __init__(
        self,
        stat_type: str = "fantasy_points",
        params: dict[str, Any] | None = None
    ):
        """
        Initialize predictor.

        Args:
            stat_type: Which stat to predict.
            params: XGBoost hyperparameters override.
        """
        if stat_type not in self.STAT_TYPES:
            raise ValueError(f"stat_type must be one of {self.STAT_TYPES}")

        self.stat_type = stat_type
        self.params = {**self.DEFAULT_PARAMS, **(params or {})}

        self.model: xgb.XGBRegressor | None = None
        self.model_lower: xgb.XGBRegressor | None = None
        self.model_upper: xgb.XGBRegressor | None = None
        self.feature_names: list[str] = []
        self.metadata: ModelMetadata | None = None
        self.logger = logging.getLogger(__name__)

    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        validation_split: float = 0.2,
        **kwargs
    ) -> "StatPredictor":
        """
        Train the XGBoost model.

        Args:
            X: Feature DataFrame.
            y: Target series.
            validation_split: Fraction for validation.
            **kwargs: Additional training parameters.

        Returns:
            Self for chaining.
        """
        self.logger.info(f"Training {self.stat_type} predictor on {len(X)} samples")

        # Store feature names
        self.feature_names = list(X.columns)

        # Prepare data (ensure numeric)
        X_clean = self._prepare_features(X)
        y_clean = y.fillna(0).values

        # Split for validation
        split_idx = int(len(X_clean) * (1 - validation_split))
        X_train, X_val = X_clean[:split_idx], X_clean[split_idx:]
        y_train, y_val = y_clean[:split_idx], y_clean[split_idx:]

        # Create eval set for early stopping
        eval_set = [(X_train, y_train), (X_val, y_val)]

        # Train main model (point prediction)
        self.model = xgb.XGBRegressor(**self.params)
        self.model.fit(
            X_train, y_train,
            eval_set=eval_set,
            verbose=False
        )

        # Train quantile models for uncertainty
        self._train_quantile_models(X_train, y_train, X_val, y_val)

        # Calculate and store metrics
        metrics = self._calculate_metrics(X_val, y_val)

        # Store metadata
        self.metadata = ModelMetadata(
            model_type="xgboost",
            target=self.stat_type,
            version="1.0.0",
            training_date=date.today(),
            training_samples=len(X_train),
            feature_count=len(self.feature_names),
            metrics=metrics,
            hyperparameters=self.params
        )

        self.logger.info(f"Training complete. Validation RMSE: {metrics.get('rmse', 'N/A'):.3f}")

        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make point predictions.

        Args:
            X: Feature DataFrame.

        Returns:
            Array of predictions.
        """
        if self.model is None:
            raise ValueError("Model not trained. Call fit() first.")

        X_clean = self._prepare_features(X)
        predictions = self.model.predict(X_clean)

        # Clip to reasonable bounds
        predictions = np.clip(predictions, 0, None)

        return predictions

    def predict_with_uncertainty(
        self,
        X: pd.DataFrame,
        confidence: float = 0.9
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Make predictions with confidence intervals.

        Args:
            X: Feature DataFrame.
            confidence: Confidence level (default 0.9 = 90% interval).

        Returns:
            Tuple of (predictions, lower_bound, upper_bound).
        """
        if self.model is None:
            raise ValueError("Model not trained. Call fit() first.")

        X_clean = self._prepare_features(X)

        # Point predictions
        predictions = self.model.predict(X_clean)

        # Quantile predictions for uncertainty
        if self.model_lower is not None and self.model_upper is not None:
            lower = self.model_lower.predict(X_clean)
            upper = self.model_upper.predict(X_clean)
        else:
            # Fallback: use standard deviation estimate
            std_estimate = predictions * 0.2  # 20% of prediction
            alpha = (1 - confidence) / 2
            z_score = 1.645  # ~90% confidence

            lower = predictions - z_score * std_estimate
            upper = predictions + z_score * std_estimate

        # Ensure bounds are reasonable
        lower = np.clip(lower, 0, None)
        upper = np.clip(upper, lower, None)

        return predictions, lower, upper

    def predict_player(
        self,
        features: dict[str, Any],
        player_id: int,
        as_of_date: date | None = None
    ) -> PredictionResult:
        """
        Make prediction for a single player.

        Args:
            features: Feature dictionary for player.
            player_id: Player database ID.
            as_of_date: Reference date.

        Returns:
            PredictionResult with prediction and uncertainty.
        """
        # Convert to DataFrame
        X = pd.DataFrame([features])

        # Get prediction with uncertainty
        pred, lower, upper = self.predict_with_uncertainty(X)

        # Calculate confidence based on interval width
        interval_width = (upper[0] - lower[0]) / (pred[0] + 1e-6)
        confidence = max(0.0, min(1.0, 1.0 - interval_width / 2))

        # Get contributing factors
        factors = self._get_prediction_factors(X.iloc[0])

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
        """
        Get feature importance scores.

        Returns:
            Dictionary mapping feature names to importance scores.
        """
        if self.model is None:
            raise ValueError("Model not trained.")

        importance = self.model.feature_importances_
        return dict(zip(self.feature_names, importance))

    def cross_validate(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        n_splits: int = 5
    ) -> dict[str, float]:
        """
        Perform time-series cross-validation.

        Args:
            X: Feature DataFrame.
            y: Target series.
            n_splits: Number of CV folds.

        Returns:
            Dictionary of CV metrics.
        """
        X_clean = self._prepare_features(X)
        y_clean = y.fillna(0).values

        tscv = TimeSeriesSplit(n_splits=n_splits)

        model = xgb.XGBRegressor(**self.params)

        scores = cross_val_score(
            model, X_clean, y_clean,
            cv=tscv,
            scoring="neg_root_mean_squared_error"
        )

        return {
            "cv_rmse_mean": -scores.mean(),
            "cv_rmse_std": scores.std(),
            "cv_scores": (-scores).tolist()
        }

    def save(self, path: str) -> None:
        """
        Save model to disk.

        Args:
            path: File path.
        """
        if self.model is None:
            raise ValueError("No model to save.")

        save_dict = {
            "model": self.model,
            "model_lower": self.model_lower,
            "model_upper": self.model_upper,
            "feature_names": self.feature_names,
            "stat_type": self.stat_type,
            "params": self.params,
            "metadata": self.metadata.to_dict() if self.metadata else None
        }

        Path(path).parent.mkdir(parents=True, exist_ok=True)

        with open(path, "wb") as f:
            pickle.dump(save_dict, f)

        self.logger.info(f"Model saved to {path}")

    def load(self, path: str) -> "StatPredictor":
        """
        Load model from disk.

        Args:
            path: File path.

        Returns:
            Self for chaining.
        """
        with open(path, "rb") as f:
            save_dict = pickle.load(f)

        self.model = save_dict["model"]
        self.model_lower = save_dict["model_lower"]
        self.model_upper = save_dict["model_upper"]
        self.feature_names = save_dict["feature_names"]
        self.stat_type = save_dict["stat_type"]
        self.params = save_dict["params"]

        if save_dict.get("metadata"):
            # Reconstruct metadata
            meta = save_dict["metadata"]
            self.metadata = ModelMetadata(
                model_type=meta["model_type"],
                target=meta["target"],
                version=meta["version"],
                training_date=date.fromisoformat(meta["training_date"]),
                training_samples=meta["training_samples"],
                feature_count=meta["feature_count"],
                metrics=meta.get("metrics"),
                hyperparameters=meta.get("hyperparameters")
            )

        self.logger.info(f"Model loaded from {path}")

        return self

    def _prepare_features(self, X: pd.DataFrame) -> np.ndarray:
        """Convert DataFrame to clean numpy array."""
        # Ensure correct column order
        if self.feature_names:
            X = X.reindex(columns=self.feature_names, fill_value=0)

        # Convert booleans to int
        for col in X.columns:
            if X[col].dtype == bool:
                X[col] = X[col].astype(int)

        # Fill missing values
        X = X.fillna(0)

        return X.values.astype(np.float32)

    def _train_quantile_models(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray
    ) -> None:
        """Train quantile regression models for uncertainty."""
        quantile_params = self.params.copy()
        quantile_params["objective"] = "reg:quantileerror"

        # Lower quantile (10th percentile)
        quantile_params["quantile_alpha"] = 0.1
        self.model_lower = xgb.XGBRegressor(**quantile_params)
        self.model_lower.fit(X_train, y_train, verbose=False)

        # Upper quantile (90th percentile)
        quantile_params["quantile_alpha"] = 0.9
        self.model_upper = xgb.XGBRegressor(**quantile_params)
        self.model_upper.fit(X_train, y_train, verbose=False)

    def _calculate_metrics(
        self,
        X_val: np.ndarray,
        y_val: np.ndarray
    ) -> dict[str, float]:
        """Calculate validation metrics."""
        predictions = self.model.predict(X_val)

        # RMSE
        rmse = np.sqrt(np.mean((predictions - y_val) ** 2))

        # MAE
        mae = np.mean(np.abs(predictions - y_val))

        # R-squared
        ss_res = np.sum((y_val - predictions) ** 2)
        ss_tot = np.sum((y_val - np.mean(y_val)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # MAPE (Mean Absolute Percentage Error)
        non_zero = y_val != 0
        if non_zero.sum() > 0:
            mape = np.mean(np.abs((y_val[non_zero] - predictions[non_zero]) / y_val[non_zero])) * 100
        else:
            mape = 0.0

        return {
            "rmse": float(rmse),
            "mae": float(mae),
            "r2": float(r2),
            "mape": float(mape),
        }

    def _get_prediction_factors(self, features: pd.Series) -> dict[str, float]:
        """
        Get top contributing factors for a prediction.

        Uses feature importance weighted by feature values.
        """
        if self.model is None:
            return {}

        importance = self.model.feature_importances_

        # Calculate contribution (importance * normalized value)
        contributions = {}
        for i, (name, value) in enumerate(features.items()):
            if i < len(importance):
                # Normalize contribution
                contrib = float(importance[i] * abs(float(value) if value else 0))
                if contrib > 0.01:  # Only include significant factors
                    contributions[name] = round(contrib, 4)

        # Return top 5 factors
        sorted_factors = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_factors[:5])
