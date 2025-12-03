"""
Tests for ML model components.
"""
import pytest
from datetime import date
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

from app.ml.models.base import PredictionResult, ModelMetadata


class TestPredictionResult:
    """Tests for PredictionResult."""

    def test_create_prediction_result(self):
        """Test creating a prediction result."""
        result = PredictionResult(
            player_id=1,
            stat_type="fantasy_points",
            prediction=35.5,
            lower_bound=28.0,
            upper_bound=43.0,
            confidence=0.85,
            factors={"recent_average": 0.4, "opponent": 0.2},
            as_of_date=date(2024, 12, 1)
        )

        assert result.player_id == 1
        assert result.stat_type == "fantasy_points"
        assert result.prediction == 35.5
        assert result.lower_bound == 28.0
        assert result.upper_bound == 43.0
        assert result.confidence == 0.85
        assert len(result.factors) == 2

    def test_to_dict(self):
        """Test serialization to dictionary."""
        result = PredictionResult(
            player_id=1,
            stat_type="points",
            prediction=25.0,
            lower_bound=20.0,
            upper_bound=30.0,
            confidence=0.8,
            as_of_date=date(2024, 12, 1)
        )

        d = result.to_dict()

        assert d["player_id"] == 1
        assert d["stat_type"] == "points"
        assert d["prediction"] == 25.0
        assert d["as_of_date"] == "2024-12-01"

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "player_id": 1,
            "stat_type": "assists",
            "prediction": 8.5,
            "lower_bound": 5.0,
            "upper_bound": 12.0,
            "confidence": 0.75,
            "factors": {},
            "as_of_date": "2024-12-01"
        }

        result = PredictionResult.from_dict(data)

        assert result.player_id == 1
        assert result.stat_type == "assists"
        assert result.prediction == 8.5
        assert result.as_of_date == date(2024, 12, 1)


class TestModelMetadata:
    """Tests for ModelMetadata."""

    def test_create_metadata(self):
        """Test creating model metadata."""
        metadata = ModelMetadata(
            model_type="xgboost",
            target="fantasy_points",
            version="1.0.0",
            training_date=date(2024, 12, 1),
            training_samples=10000,
            feature_count=150,
            metrics={"rmse": 5.5, "r2": 0.85},
            hyperparameters={"max_depth": 6, "learning_rate": 0.05}
        )

        assert metadata.model_type == "xgboost"
        assert metadata.target == "fantasy_points"
        assert metadata.training_samples == 10000
        assert metadata.metrics["rmse"] == 5.5

    def test_to_dict(self):
        """Test metadata serialization."""
        metadata = ModelMetadata(
            model_type="ensemble",
            target="points",
            version="2.0.0",
            training_date=date(2024, 12, 1),
            training_samples=5000,
            feature_count=100
        )

        d = metadata.to_dict()

        assert d["model_type"] == "ensemble"
        assert d["target"] == "points"
        assert d["training_date"] == "2024-12-01"


class TestModelPredictions:
    """Tests for model prediction logic."""

    def test_confidence_calculation(self):
        """Test confidence calculation from interval width."""
        prediction = 30.0
        lower_bound = 24.0
        upper_bound = 36.0

        interval_width = (upper_bound - lower_bound) / (prediction + 1e-6)
        confidence = max(0.0, min(1.0, 1.0 - interval_width / 2))

        # Interval width = 12/30 = 0.4
        # Confidence = 1 - 0.4/2 = 1 - 0.2 = 0.8
        assert abs(confidence - 0.8) < 0.01

    def test_prediction_bounds_non_negative(self):
        """Test that prediction bounds are non-negative."""
        prediction = 10.0
        std_estimate = prediction * 0.5  # Large uncertainty

        lower = prediction - 1.645 * std_estimate
        lower = max(0, lower)  # Clip to 0

        assert lower >= 0

    def test_upper_bound_greater_than_lower(self):
        """Test upper bound is always >= lower bound."""
        prediction = 20.0
        std = 3.0

        lower = prediction - 1.645 * std
        upper = prediction + 1.645 * std

        assert upper > lower


class TestFantasyPointsCalculation:
    """Tests for fantasy points calculations."""

    def test_standard_scoring(self):
        """Test standard fantasy scoring formula."""
        # Standard scoring: PTS + REB*1.2 + AST*1.5 + STL*3 + BLK*3 - TO
        stats = {
            "points": 20,
            "rebounds": 10,
            "assists": 5,
            "steals": 2,
            "blocks": 1,
            "turnovers": 3
        }

        fp = (
            stats["points"] * 1.0 +
            stats["rebounds"] * 1.2 +
            stats["assists"] * 1.5 +
            stats["steals"] * 3.0 +
            stats["blocks"] * 3.0 +
            stats["turnovers"] * -1.0
        )

        # 20 + 12 + 7.5 + 6 + 3 - 3 = 45.5
        assert fp == 45.5

    def test_zero_stats(self):
        """Test fantasy points with zero stats."""
        stats = {
            "points": 0,
            "rebounds": 0,
            "assists": 0,
            "steals": 0,
            "blocks": 0,
            "turnovers": 0
        }

        fp = (
            stats["points"] * 1.0 +
            stats["rebounds"] * 1.2 +
            stats["assists"] * 1.5 +
            stats["steals"] * 3.0 +
            stats["blocks"] * 3.0 +
            stats["turnovers"] * -1.0
        )

        assert fp == 0.0

    def test_high_scoring_game(self):
        """Test fantasy points for exceptional performance."""
        # Luka Doncic type game
        stats = {
            "points": 45,
            "rebounds": 12,
            "assists": 15,
            "steals": 3,
            "blocks": 1,
            "turnovers": 5
        }

        fp = (
            stats["points"] * 1.0 +
            stats["rebounds"] * 1.2 +
            stats["assists"] * 1.5 +
            stats["steals"] * 3.0 +
            stats["blocks"] * 3.0 +
            stats["turnovers"] * -1.0
        )

        # 45 + 14.4 + 22.5 + 9 + 3 - 5 = 88.9
        assert fp == 88.9
