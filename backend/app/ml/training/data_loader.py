"""
Training data loader.

Handles data preparation for model training.
"""
import logging
from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.game_stats import PlayerGameStats
from app.ml.features.engineer import FeatureEngineer

logger = logging.getLogger(__name__)


class TrainingDataLoader:
    """
    Loader for preparing training datasets.

    Handles feature generation and target variable extraction
    for model training pipelines.
    """

    # Minimum games required for a player to be included
    MIN_GAMES = 10

    # Lookback days for features
    FEATURE_LOOKBACK = 90

    def __init__(self, db: Session):
        """
        Initialize data loader.

        Args:
            db: Database session.
        """
        self.db = db
        self.feature_engineer = FeatureEngineer(db)
        self.logger = logging.getLogger(__name__)

    def load_training_data(
        self,
        start_date: date,
        end_date: date,
        stat_type: str = "fantasy_points",
        min_games: int | None = None
    ) -> tuple[pd.DataFrame, pd.Series]:
        """
        Load training data for a date range.

        Args:
            start_date: Start of training period.
            end_date: End of training period.
            stat_type: Target stat to predict.
            min_games: Minimum games for player inclusion.

        Returns:
            Tuple of (features DataFrame, target Series).
        """
        min_games = min_games or self.MIN_GAMES

        self.logger.info(f"Loading training data from {start_date} to {end_date}")

        # Get eligible players
        player_ids = self._get_eligible_players(start_date, end_date, min_games)
        self.logger.info(f"Found {len(player_ids)} eligible players")

        # Get game dates in range
        game_dates = self._get_game_dates(start_date, end_date)
        self.logger.info(f"Found {len(game_dates)} game dates")

        # Build training examples
        features_list = []
        targets_list = []

        for game_date in game_dates:
            # Get players who played on this date
            players_played = self._get_players_on_date(player_ids, game_date)

            for player_id, actual_stat in players_played:
                try:
                    # Build features as of game date (using prior data)
                    features = self.feature_engineer.build_player_features(
                        player_id, game_date, lookback_days=self.FEATURE_LOOKBACK
                    )

                    if not features:
                        continue

                    # Add metadata
                    features["player_id"] = player_id
                    features["game_date"] = game_date

                    features_list.append(features)
                    targets_list.append(actual_stat)

                except Exception as e:
                    self.logger.warning(f"Failed to process {player_id} on {game_date}: {e}")

        self.logger.info(f"Generated {len(features_list)} training examples")

        # Create DataFrames
        X = pd.DataFrame(features_list)
        y = pd.Series(targets_list, name=stat_type)

        # Remove metadata columns from features
        feature_cols = [c for c in X.columns if c not in ["player_id", "game_date"]]
        X = X[feature_cols]

        return X, y

    def load_validation_data(
        self,
        validation_date: date,
        stat_type: str = "fantasy_points"
    ) -> tuple[pd.DataFrame, pd.Series, list[int]]:
        """
        Load validation data for a specific date.

        Args:
            validation_date: Date to validate on.
            stat_type: Target stat.

        Returns:
            Tuple of (features, targets, player_ids).
        """
        # Get all games on that date
        games = self.db.query(
            PlayerGameStats.player_id,
            getattr(PlayerGameStats, stat_type)
        ).filter(
            PlayerGameStats.game_date == validation_date
        ).all()

        features_list = []
        targets_list = []
        player_ids = []

        for player_id, actual in games:
            if actual is None:
                continue

            try:
                features = self.feature_engineer.build_player_features(
                    player_id, validation_date, lookback_days=self.FEATURE_LOOKBACK
                )

                if not features:
                    continue

                features_list.append(features)
                targets_list.append(actual)
                player_ids.append(player_id)

            except Exception as e:
                self.logger.warning(f"Validation data failed for {player_id}: {e}")

        X = pd.DataFrame(features_list)
        y = pd.Series(targets_list, name=stat_type)

        return X, y, player_ids

    def create_time_series_splits(
        self,
        start_date: date,
        end_date: date,
        n_splits: int = 5,
        test_days: int = 14
    ) -> list[tuple[date, date, date, date]]:
        """
        Create time-series cross-validation splits.

        Args:
            start_date: Overall start date.
            end_date: Overall end date.
            n_splits: Number of splits.
            test_days: Days in each test period.

        Returns:
            List of (train_start, train_end, test_start, test_end) tuples.
        """
        total_days = (end_date - start_date).days
        split_size = total_days // (n_splits + 1)

        splits = []

        for i in range(n_splits):
            train_start = start_date
            train_end = start_date + timedelta(days=split_size * (i + 1))
            test_start = train_end + timedelta(days=1)
            test_end = min(test_start + timedelta(days=test_days), end_date)

            splits.append((train_start, train_end, test_start, test_end))

        return splits

    def get_feature_statistics(
        self,
        X: pd.DataFrame
    ) -> dict[str, dict[str, float]]:
        """
        Calculate feature statistics for normalization.

        Args:
            X: Feature DataFrame.

        Returns:
            Dictionary of feature -> {mean, std, min, max}.
        """
        stats = {}

        for col in X.columns:
            if X[col].dtype in [np.float64, np.float32, np.int64, np.int32]:
                stats[col] = {
                    "mean": float(X[col].mean()),
                    "std": float(X[col].std()),
                    "min": float(X[col].min()),
                    "max": float(X[col].max()),
                }

        return stats

    def _get_eligible_players(
        self,
        start_date: date,
        end_date: date,
        min_games: int
    ) -> list[int]:
        """Get players with sufficient games in period."""
        player_games = self.db.query(
            PlayerGameStats.player_id,
            func.count(PlayerGameStats.id).label("game_count")
        ).filter(
            PlayerGameStats.game_date >= start_date,
            PlayerGameStats.game_date <= end_date
        ).group_by(
            PlayerGameStats.player_id
        ).having(
            func.count(PlayerGameStats.id) >= min_games
        ).all()

        return [p.player_id for p in player_games]

    def _get_game_dates(self, start_date: date, end_date: date) -> list[date]:
        """Get unique game dates in range."""
        dates = self.db.query(
            func.distinct(PlayerGameStats.game_date)
        ).filter(
            PlayerGameStats.game_date >= start_date,
            PlayerGameStats.game_date <= end_date
        ).order_by(
            PlayerGameStats.game_date
        ).all()

        return [d[0] for d in dates]

    def _get_players_on_date(
        self,
        player_ids: list[int],
        game_date: date
    ) -> list[tuple[int, float]]:
        """Get players who played on a specific date with their stats."""
        games = self.db.query(
            PlayerGameStats.player_id,
            PlayerGameStats.fantasy_points
        ).filter(
            PlayerGameStats.player_id.in_(player_ids),
            PlayerGameStats.game_date == game_date,
            PlayerGameStats.fantasy_points.isnot(None)
        ).all()

        return [(g.player_id, g.fantasy_points) for g in games]


class DataAugmentation:
    """
    Data augmentation utilities for training.

    Helps improve model robustness with synthetic variations.
    """

    @staticmethod
    def add_noise(
        X: pd.DataFrame,
        noise_level: float = 0.05
    ) -> pd.DataFrame:
        """
        Add Gaussian noise to numeric features.

        Args:
            X: Feature DataFrame.
            noise_level: Noise standard deviation as fraction of feature std.

        Returns:
            Augmented DataFrame.
        """
        X_aug = X.copy()

        for col in X_aug.columns:
            if X_aug[col].dtype in [np.float64, np.float32]:
                std = X_aug[col].std()
                noise = np.random.normal(0, std * noise_level, len(X_aug))
                X_aug[col] = X_aug[col] + noise

        return X_aug

    @staticmethod
    def bootstrap_sample(
        X: pd.DataFrame,
        y: pd.Series,
        n_samples: int | None = None
    ) -> tuple[pd.DataFrame, pd.Series]:
        """
        Create bootstrap sample.

        Args:
            X: Feature DataFrame.
            y: Target Series.
            n_samples: Number of samples (defaults to original size).

        Returns:
            Bootstrapped (X, y).
        """
        n_samples = n_samples or len(X)
        indices = np.random.choice(len(X), size=n_samples, replace=True)

        return X.iloc[indices].reset_index(drop=True), y.iloc[indices].reset_index(drop=True)
