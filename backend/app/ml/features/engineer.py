"""
Feature engineering pipeline for player stat predictions.

Generates features from historical game data for ML models.
"""
import logging
from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.game_stats import PlayerGameStats
from app.models.team import Team

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Feature engineering pipeline for fantasy basketball predictions.

    Generates player-level and game context features from historical data.
    """

    # Rolling window configurations
    ROLLING_WINDOWS = [3, 5, 10, 15, 30]

    # Core stat columns for feature generation
    STAT_COLUMNS = [
        "points", "rebounds", "assists", "steals", "blocks",
        "turnovers", "minutes", "field_goals_made", "field_goals_attempted",
        "three_pointers_made", "three_pointers_attempted",
        "free_throws_made", "free_throws_attempted", "fantasy_points"
    ]

    # Derived ratio columns
    RATIO_COLUMNS = [
        ("field_goal_pct", "field_goals_made", "field_goals_attempted"),
        ("three_point_pct", "three_pointers_made", "three_pointers_attempted"),
        ("free_throw_pct", "free_throws_made", "free_throws_attempted"),
    ]

    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def build_player_features(
        self,
        player_id: int,
        as_of_date: date,
        lookback_days: int = 90
    ) -> dict[str, Any]:
        """
        Build feature vector for a player as of a specific date.

        Args:
            player_id: Database player ID.
            as_of_date: Date for which to generate features.
            lookback_days: Number of days to look back for historical stats.

        Returns:
            Dictionary of feature names to values.
        """
        # Get player info
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise ValueError(f"Player {player_id} not found")

        # Get historical stats
        start_date = as_of_date - timedelta(days=lookback_days)
        stats = self._get_player_stats(player_id, start_date, as_of_date)

        if stats.empty:
            self.logger.warning(f"No stats for player {player_id} before {as_of_date}")
            return self._get_empty_features(player)

        features = {}

        # Basic player features
        features.update(self._build_player_info_features(player))

        # Rolling average features
        features.update(self._build_rolling_features(stats))

        # Trend features
        features.update(self._build_trend_features(stats))

        # Consistency features
        features.update(self._build_consistency_features(stats))

        # Usage features
        features.update(self._build_usage_features(stats))

        # Rest/fatigue features
        features.update(self._build_rest_features(stats, as_of_date))

        # Recent form features
        features.update(self._build_form_features(stats))

        return features

    def build_batch_features(
        self,
        player_ids: list[int],
        as_of_date: date,
        lookback_days: int = 90
    ) -> pd.DataFrame:
        """
        Build features for multiple players efficiently.

        Args:
            player_ids: List of player IDs.
            as_of_date: Target date.
            lookback_days: Lookback window.

        Returns:
            DataFrame with player features.
        """
        features_list = []

        for player_id in player_ids:
            try:
                features = self.build_player_features(player_id, as_of_date, lookback_days)
                features["player_id"] = player_id
                features["as_of_date"] = as_of_date
                features_list.append(features)
            except Exception as e:
                self.logger.error(f"Failed to build features for player {player_id}: {e}")

        return pd.DataFrame(features_list)

    def _get_player_stats(
        self,
        player_id: int,
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """Fetch player stats as DataFrame."""
        stats = self.db.query(PlayerGameStats).filter(
            PlayerGameStats.player_id == player_id,
            PlayerGameStats.game_date >= start_date,
            PlayerGameStats.game_date < end_date
        ).order_by(PlayerGameStats.game_date.desc()).all()

        if not stats:
            return pd.DataFrame()

        records = []
        for s in stats:
            record = {
                "game_date": s.game_date,
                "minutes": s.minutes or 0,
                "points": s.points or 0,
                "rebounds": s.rebounds or 0,
                "assists": s.assists or 0,
                "steals": s.steals or 0,
                "blocks": s.blocks or 0,
                "turnovers": s.turnovers or 0,
                "field_goals_made": s.field_goals_made or 0,
                "field_goals_attempted": s.field_goals_attempted or 0,
                "three_pointers_made": s.three_pointers_made or 0,
                "three_pointers_attempted": s.three_pointers_attempted or 0,
                "free_throws_made": s.free_throws_made or 0,
                "free_throws_attempted": s.free_throws_attempted or 0,
                "fantasy_points": s.fantasy_points or 0,
            }
            records.append(record)

        df = pd.DataFrame(records)
        df = df.sort_values("game_date", ascending=True).reset_index(drop=True)
        return df

    def _build_player_info_features(self, player: Player) -> dict[str, Any]:
        """Build features from player info."""
        features = {
            "player_position_pg": player.position == "PG" if player.position else False,
            "player_position_sg": player.position == "SG" if player.position else False,
            "player_position_sf": player.position == "SF" if player.position else False,
            "player_position_pf": player.position == "PF" if player.position else False,
            "player_position_c": player.position == "C" if player.position else False,
        }

        # Age feature (if birth_date available)
        if player.birth_date:
            age = (date.today() - player.birth_date).days / 365.25
            features["player_age"] = age
        else:
            features["player_age"] = 27.0  # Default NBA average

        return features

    def _build_rolling_features(self, stats: pd.DataFrame) -> dict[str, float]:
        """Build rolling average features for different windows."""
        features = {}

        for window in self.ROLLING_WINDOWS:
            if len(stats) >= window:
                recent = stats.tail(window)
            else:
                recent = stats

            for col in self.STAT_COLUMNS:
                if col in stats.columns:
                    features[f"{col}_avg_{window}g"] = recent[col].mean()

        # Add shooting percentages
        for name, made, attempted in self.RATIO_COLUMNS:
            for window in self.ROLLING_WINDOWS:
                if len(stats) >= window:
                    recent = stats.tail(window)
                else:
                    recent = stats

                total_made = recent[made].sum()
                total_attempted = recent[attempted].sum()

                if total_attempted > 0:
                    features[f"{name}_{window}g"] = total_made / total_attempted
                else:
                    features[f"{name}_{window}g"] = 0.0

        return features

    def _build_trend_features(self, stats: pd.DataFrame) -> dict[str, float]:
        """Build trend features comparing recent to season."""
        features = {}

        if len(stats) < 10:
            for col in self.STAT_COLUMNS:
                features[f"{col}_trend"] = 0.0
            return features

        recent_5 = stats.tail(5)
        season = stats

        for col in self.STAT_COLUMNS:
            if col in stats.columns:
                recent_avg = recent_5[col].mean()
                season_avg = season[col].mean()

                if season_avg > 0:
                    features[f"{col}_trend"] = (recent_avg - season_avg) / season_avg
                else:
                    features[f"{col}_trend"] = 0.0

        return features

    def _build_consistency_features(self, stats: pd.DataFrame) -> dict[str, float]:
        """Build consistency/variance features."""
        features = {}

        for col in self.STAT_COLUMNS:
            if col in stats.columns:
                # Coefficient of variation (lower = more consistent)
                mean = stats[col].mean()
                std = stats[col].std()

                if mean > 0 and not np.isnan(std):
                    features[f"{col}_cv"] = std / mean
                else:
                    features[f"{col}_cv"] = 0.0

                # Standard deviation
                features[f"{col}_std"] = std if not np.isnan(std) else 0.0

        return features

    def _build_usage_features(self, stats: pd.DataFrame) -> dict[str, float]:
        """Build usage pattern features."""
        features = {}

        # Games played
        features["games_played"] = len(stats)

        # Average minutes (proxy for role)
        features["avg_minutes_season"] = stats["minutes"].mean()

        # Shot attempts per game (usage indicator)
        features["fga_per_game"] = stats["field_goals_attempted"].mean()
        features["fta_per_game"] = stats["free_throws_attempted"].mean()

        # Assist to turnover ratio
        total_assists = stats["assists"].sum()
        total_turnovers = stats["turnovers"].sum()

        if total_turnovers > 0:
            features["ast_to_ratio"] = total_assists / total_turnovers
        else:
            features["ast_to_ratio"] = total_assists

        return features

    def _build_rest_features(self, stats: pd.DataFrame, as_of_date: date) -> dict[str, float]:
        """Build rest and fatigue features."""
        features = {}

        if stats.empty:
            features["days_rest"] = 3.0  # Default
            features["games_last_7d"] = 0
            features["games_last_14d"] = 0
            features["back_to_back"] = False
            return features

        # Days since last game
        last_game_date = stats["game_date"].max()
        features["days_rest"] = (as_of_date - last_game_date).days

        # Games in last week/two weeks (fatigue)
        week_ago = as_of_date - timedelta(days=7)
        two_weeks_ago = as_of_date - timedelta(days=14)

        features["games_last_7d"] = len(stats[stats["game_date"] >= week_ago])
        features["games_last_14d"] = len(stats[stats["game_date"] >= two_weeks_ago])

        # Back-to-back detection
        features["back_to_back"] = features["days_rest"] == 1

        return features

    def _build_form_features(self, stats: pd.DataFrame) -> dict[str, float]:
        """Build recent form indicators."""
        features = {}

        if len(stats) < 3:
            features["hot_streak"] = False
            features["cold_streak"] = False
            features["fantasy_momentum"] = 0.0
            return features

        # Fantasy points momentum
        recent_3 = stats.tail(3)
        season_avg = stats["fantasy_points"].mean()
        recent_avg = recent_3["fantasy_points"].mean()

        if season_avg > 0:
            features["fantasy_momentum"] = (recent_avg - season_avg) / season_avg
        else:
            features["fantasy_momentum"] = 0.0

        # Streak detection
        recent_3_fp = recent_3["fantasy_points"].values

        # Hot streak: last 3 games all above season average
        features["hot_streak"] = all(fp > season_avg for fp in recent_3_fp)

        # Cold streak: last 3 games all below season average
        features["cold_streak"] = all(fp < season_avg for fp in recent_3_fp)

        return features

    def _get_empty_features(self, player: Player) -> dict[str, Any]:
        """Return empty/default features for players with no stats."""
        features = self._build_player_info_features(player)

        # Set all stat features to 0 or reasonable defaults
        for window in self.ROLLING_WINDOWS:
            for col in self.STAT_COLUMNS:
                features[f"{col}_avg_{window}g"] = 0.0

            for name, _, _ in self.RATIO_COLUMNS:
                features[f"{name}_{window}g"] = 0.0

        for col in self.STAT_COLUMNS:
            features[f"{col}_trend"] = 0.0
            features[f"{col}_cv"] = 0.0
            features[f"{col}_std"] = 0.0

        features["games_played"] = 0
        features["avg_minutes_season"] = 0.0
        features["fga_per_game"] = 0.0
        features["fta_per_game"] = 0.0
        features["ast_to_ratio"] = 0.0
        features["days_rest"] = 3.0
        features["games_last_7d"] = 0
        features["games_last_14d"] = 0
        features["back_to_back"] = False
        features["hot_streak"] = False
        features["cold_streak"] = False
        features["fantasy_momentum"] = 0.0

        return features


class GameContextFeatureBuilder:
    """
    Builds game context features for predictions.

    Includes opponent strength, home/away, schedule factors.
    """

    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def build_opponent_features(
        self,
        opponent_team_id: int,
        position: str | None = None
    ) -> dict[str, float]:
        """
        Build opponent-based features.

        Args:
            opponent_team_id: Database team ID.
            position: Player position for matchup analysis.

        Returns:
            Dictionary of opponent features.
        """
        features = {}

        # Get opponent's defensive stats (placeholder - would need more data)
        features["opp_defensive_rating"] = 110.0  # Default NBA average
        features["opp_pace"] = 100.0  # Default pace

        # Position-specific opponent features would go here
        # These would require opponent player tracking

        return features

    def build_schedule_features(
        self,
        player_id: int,
        game_date: date
    ) -> dict[str, Any]:
        """
        Build schedule-based features.

        Args:
            player_id: Database player ID.
            game_date: Date of the game.

        Returns:
            Dictionary of schedule features.
        """
        features = {}

        # Day of week
        features["is_weekend"] = game_date.weekday() >= 5
        features["day_of_week"] = game_date.weekday()

        # Month (for seasonal patterns)
        features["month"] = game_date.month

        # Part of season (early, mid, late, playoffs)
        if game_date.month in [10, 11, 12]:
            features["season_phase"] = "early"
        elif game_date.month in [1, 2]:
            features["season_phase"] = "mid"
        elif game_date.month == 3:
            features["season_phase"] = "late"
        else:
            features["season_phase"] = "playoffs"

        return features
