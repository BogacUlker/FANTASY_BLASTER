"""
Base predictor interface.

Defines the contract for all prediction models.
"""
from abc import ABC, abstractmethod
from datetime import date
from typing import Any

import numpy as np
import pandas as pd


class BasePredictor(ABC):
    """
    Abstract base class for all predictors.

    Defines the interface for model training and prediction.
    """

    @abstractmethod
    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        **kwargs
    ) -> "BasePredictor":
        """
        Train the model.

        Args:
            X: Feature DataFrame.
            y: Target series.
            **kwargs: Additional training parameters.

        Returns:
            Self for chaining.
        """
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions.

        Args:
            X: Feature DataFrame.

        Returns:
            Array of predictions.
        """
        pass

    @abstractmethod
    def predict_with_uncertainty(
        self,
        X: pd.DataFrame
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Make predictions with uncertainty estimates.

        Args:
            X: Feature DataFrame.

        Returns:
            Tuple of (predictions, lower_bound, upper_bound).
        """
        pass

    @abstractmethod
    def get_feature_importance(self) -> dict[str, float]:
        """
        Get feature importance scores.

        Returns:
            Dictionary mapping feature names to importance scores.
        """
        pass

    @abstractmethod
    def save(self, path: str) -> None:
        """
        Save model to disk.

        Args:
            path: File path to save model.
        """
        pass

    @abstractmethod
    def load(self, path: str) -> "BasePredictor":
        """
        Load model from disk.

        Args:
            path: File path to load model from.

        Returns:
            Self for chaining.
        """
        pass


class PredictionResult:
    """
    Container for prediction results.

    Holds prediction value along with confidence and contributing factors.
    """

    def __init__(
        self,
        player_id: int,
        stat_type: str,
        prediction: float,
        lower_bound: float,
        upper_bound: float,
        confidence: float,
        factors: dict[str, float] | None = None,
        as_of_date: date | None = None
    ):
        self.player_id = player_id
        self.stat_type = stat_type
        self.prediction = prediction
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.confidence = confidence
        self.factors = factors or {}
        self.as_of_date = as_of_date

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "player_id": self.player_id,
            "stat_type": self.stat_type,
            "prediction": self.prediction,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "confidence": self.confidence,
            "factors": self.factors,
            "as_of_date": self.as_of_date.isoformat() if self.as_of_date else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PredictionResult":
        """Create from dictionary."""
        as_of_date = None
        if data.get("as_of_date"):
            as_of_date = date.fromisoformat(data["as_of_date"])

        return cls(
            player_id=data["player_id"],
            stat_type=data["stat_type"],
            prediction=data["prediction"],
            lower_bound=data["lower_bound"],
            upper_bound=data["upper_bound"],
            confidence=data["confidence"],
            factors=data.get("factors", {}),
            as_of_date=as_of_date,
        )


class ModelMetadata:
    """
    Metadata for trained models.

    Tracks training parameters, performance metrics, and versioning.
    """

    def __init__(
        self,
        model_type: str,
        target: str,
        version: str,
        training_date: date,
        training_samples: int,
        feature_count: int,
        metrics: dict[str, float] | None = None,
        hyperparameters: dict[str, Any] | None = None
    ):
        self.model_type = model_type
        self.target = target
        self.version = version
        self.training_date = training_date
        self.training_samples = training_samples
        self.feature_count = feature_count
        self.metrics = metrics or {}
        self.hyperparameters = hyperparameters or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_type": self.model_type,
            "target": self.target,
            "version": self.version,
            "training_date": self.training_date.isoformat(),
            "training_samples": self.training_samples,
            "feature_count": self.feature_count,
            "metrics": self.metrics,
            "hyperparameters": self.hyperparameters,
        }
