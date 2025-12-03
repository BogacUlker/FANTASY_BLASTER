"""Prediction serving components."""

from app.ml.serving.prediction_service import PredictionService
from app.ml.serving.model_registry import ModelRegistry

__all__ = ["PredictionService", "ModelRegistry"]
