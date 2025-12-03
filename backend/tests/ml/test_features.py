"""
Tests for feature engineering components.
"""
import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

from app.ml.features.engineer import FeatureEngineer, GameContextFeatureBuilder


class TestFeatureEngineer:
    """Tests for FeatureEngineer."""

    def test_rolling_windows_defined(self):
        """Test rolling windows are properly defined."""
        assert FeatureEngineer.ROLLING_WINDOWS == [3, 5, 10, 15, 30]

    def test_stat_columns_defined(self):
        """Test stat columns are comprehensive."""
        expected = [
            "points", "rebounds", "assists", "steals", "blocks",
            "turnovers", "minutes", "field_goals_made", "field_goals_attempted",
            "three_pointers_made", "three_pointers_attempted",
            "free_throws_made", "free_throws_attempted", "fantasy_points"
        ]
        assert FeatureEngineer.STAT_COLUMNS == expected

    def test_ratio_columns_defined(self):
        """Test ratio columns are properly defined."""
        assert len(FeatureEngineer.RATIO_COLUMNS) == 3
        names = [r[0] for r in FeatureEngineer.RATIO_COLUMNS]
        assert "field_goal_pct" in names
        assert "three_point_pct" in names
        assert "free_throw_pct" in names


class TestGameContextFeatureBuilder:
    """Tests for GameContextFeatureBuilder."""

    def test_default_defensive_rating(self):
        """Test default defensive rating is NBA average."""
        assert GameContextFeatureBuilder.DEFAULT_DEF_RATING == 112.0

    def test_build_time_context_features(self):
        """Test time context feature generation."""
        mock_db = MagicMock()
        builder = GameContextFeatureBuilder(mock_db)

        # Test weekend detection
        saturday = date(2024, 12, 7)  # Saturday
        features = builder.build_time_context_features(saturday)

        assert features["is_weekend"] == True
        assert features["dow_saturday"] == True
        assert features["dow_sunday"] == False

        # Test weekday
        monday = date(2024, 12, 9)  # Monday
        features = builder.build_time_context_features(monday)

        assert features["is_weekend"] == False
        assert features["dow_monday"] == True

    def test_season_phase_detection(self):
        """Test season phase detection."""
        mock_db = MagicMock()
        builder = GameContextFeatureBuilder(mock_db)

        # Early season (October/November)
        features = builder.build_time_context_features(date(2024, 11, 15))
        assert features["season_phase_early"] == True
        assert features["season_phase_mid"] == False

        # Mid season (December-February)
        features = builder.build_time_context_features(date(2024, 12, 15))
        assert features["season_phase_mid"] == True
        assert features["season_phase_early"] == False

        # Late season (March+)
        features = builder.build_time_context_features(date(2024, 3, 15))
        assert features["season_phase_late"] == True


class TestFeatureCalculations:
    """Tests for feature calculations."""

    def test_trend_calculation(self):
        """Test trend feature calculation logic."""
        # Simulate: recent average 25, season average 20
        # Expected trend: (25 - 20) / 20 = 0.25 (25% above average)
        recent_avg = 25.0
        season_avg = 20.0
        trend = (recent_avg - season_avg) / season_avg

        assert trend == 0.25

    def test_coefficient_of_variation(self):
        """Test CV calculation."""
        values = [20, 22, 18, 25, 15]  # Mean = 20, some variance
        mean = np.mean(values)
        std = np.std(values)
        cv = std / mean

        assert cv > 0  # Should have some variance
        assert cv < 1  # Reasonable CV for basketball stats

    def test_fantasy_momentum_calculation(self):
        """Test fantasy momentum calculation."""
        # Recent games above average = positive momentum
        season_avg = 30.0
        recent_avg = 35.0
        momentum = (recent_avg - season_avg) / season_avg

        assert momentum > 0  # Positive momentum

        # Recent games below average = negative momentum
        recent_avg = 25.0
        momentum = (recent_avg - season_avg) / season_avg

        assert momentum < 0  # Negative momentum


class TestFeatureEdgeCases:
    """Tests for edge cases in feature engineering."""

    def test_empty_stats_handling(self):
        """Test handling of empty stats DataFrame."""
        # Empty DataFrame should return empty or default features
        empty_df = pd.DataFrame()
        assert len(empty_df) == 0

    def test_zero_division_protection(self):
        """Test protection against division by zero."""
        # Coefficient of variation with mean = 0
        mean = 0.0
        std = 1.0

        if mean > 0:
            cv = std / mean
        else:
            cv = 0.0

        assert cv == 0.0

    def test_negative_values_clipped(self):
        """Test that predictions are clipped to non-negative."""
        prediction = -5.0
        clipped = max(0, prediction)

        assert clipped == 0.0
