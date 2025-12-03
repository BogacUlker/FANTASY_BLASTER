"""
Player-specific feature builders.

Handles individual player feature extraction and transformation.
"""
import logging
from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.models.player import Player, InjuryStatus
from app.models.game_stats import PlayerGameStats

logger = logging.getLogger(__name__)


class PlayerFeatureBuilder:
    """
    Builder for player-specific features.

    Handles player-level feature extraction including
    injury history, role changes, and performance patterns.
    """

    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def build_injury_features(self, player: Player) -> dict[str, Any]:
        """
        Build injury-related features.

        Args:
            player: Player model instance.

        Returns:
            Dictionary of injury features.
        """
        features = {}

        # Current injury status
        features["is_injured"] = player.injury_status != InjuryStatus.HEALTHY
        features["injury_status_gtd"] = player.injury_status == InjuryStatus.GTD
        features["injury_status_out"] = player.injury_status == InjuryStatus.OUT
        features["injury_status_doubtful"] = player.injury_status == InjuryStatus.DOUBTFUL

        return features

    def build_role_features(
        self,
        player_id: int,
        as_of_date: date
    ) -> dict[str, float]:
        """
        Build features indicating player's role changes.

        Args:
            player_id: Database player ID.
            as_of_date: Reference date.

        Returns:
            Dictionary of role features.
        """
        features = {}

        # Get recent games
        recent_games = self._get_recent_games(player_id, as_of_date, days=30)

        if len(recent_games) < 5:
            features["minutes_trend"] = 0.0
            features["usage_trend"] = 0.0
            features["starting_pct"] = 0.5
            return features

        # Minutes trend (increasing role)
        first_half = recent_games.head(len(recent_games) // 2)
        second_half = recent_games.tail(len(recent_games) // 2)

        first_minutes = first_half["minutes"].mean()
        second_minutes = second_half["minutes"].mean()

        if first_minutes > 0:
            features["minutes_trend"] = (second_minutes - first_minutes) / first_minutes
        else:
            features["minutes_trend"] = 0.0

        # Usage trend (shot attempts per minute)
        first_usage = (first_half["field_goals_attempted"] / first_half["minutes"].replace(0, 1)).mean()
        second_usage = (second_half["field_goals_attempted"] / second_half["minutes"].replace(0, 1)).mean()

        if first_usage > 0:
            features["usage_trend"] = (second_usage - first_usage) / first_usage
        else:
            features["usage_trend"] = 0.0

        # Starting percentage (high minutes games)
        features["starting_pct"] = (recent_games["minutes"] >= 20).mean()

        return features

    def build_home_away_splits(
        self,
        player_id: int,
        is_home: bool,
        as_of_date: date
    ) -> dict[str, float]:
        """
        Build home/away performance split features.

        Args:
            player_id: Database player ID.
            is_home: Whether next game is home.
            as_of_date: Reference date.

        Returns:
            Dictionary of split features.
        """
        features = {}

        # Note: Would need home/away flag on game stats
        # For now, return default features
        features["is_home_game"] = is_home
        features["home_fp_boost"] = 0.02 if is_home else -0.02  # Typical home advantage

        return features

    def build_matchup_features(
        self,
        player_id: int,
        opponent_team_id: int,
        as_of_date: date
    ) -> dict[str, float]:
        """
        Build historical matchup features.

        Args:
            player_id: Database player ID.
            opponent_team_id: Opponent team ID.
            as_of_date: Reference date.

        Returns:
            Dictionary of matchup features.
        """
        features = {}

        # Get games against this opponent
        # Note: Would need opponent_team_id on game stats
        # For now, return default features

        features["vs_opponent_games"] = 0
        features["vs_opponent_fp_avg"] = 0.0
        features["vs_opponent_fp_boost"] = 0.0

        return features

    def build_per_minute_features(
        self,
        player_id: int,
        as_of_date: date
    ) -> dict[str, float]:
        """
        Build per-minute rate features.

        Args:
            player_id: Database player ID.
            as_of_date: Reference date.

        Returns:
            Dictionary of rate features.
        """
        features = {}

        recent_games = self._get_recent_games(player_id, as_of_date, days=30)

        if recent_games.empty or recent_games["minutes"].sum() == 0:
            features["pts_per_min"] = 0.0
            features["reb_per_min"] = 0.0
            features["ast_per_min"] = 0.0
            features["fp_per_min"] = 0.0
            return features

        total_minutes = recent_games["minutes"].sum()

        features["pts_per_min"] = recent_games["points"].sum() / total_minutes
        features["reb_per_min"] = recent_games["rebounds"].sum() / total_minutes
        features["ast_per_min"] = recent_games["assists"].sum() / total_minutes
        features["fp_per_min"] = recent_games["fantasy_points"].sum() / total_minutes

        return features

    def build_ceiling_floor_features(
        self,
        player_id: int,
        as_of_date: date
    ) -> dict[str, float]:
        """
        Build ceiling/floor projection features.

        Args:
            player_id: Database player ID.
            as_of_date: Reference date.

        Returns:
            Dictionary of ceiling/floor features.
        """
        features = {}

        recent_games = self._get_recent_games(player_id, as_of_date, days=60)

        if len(recent_games) < 5:
            features["fp_ceiling"] = 0.0
            features["fp_floor"] = 0.0
            features["fp_range"] = 0.0
            features["upside_games_pct"] = 0.0
            return features

        fp = recent_games["fantasy_points"]

        # Ceiling: 90th percentile
        features["fp_ceiling"] = np.percentile(fp, 90)

        # Floor: 10th percentile
        features["fp_floor"] = np.percentile(fp, 10)

        # Range
        features["fp_range"] = features["fp_ceiling"] - features["fp_floor"]

        # Upside games percentage (games above 75th percentile)
        p75 = np.percentile(fp, 75)
        features["upside_games_pct"] = (fp > p75).mean()

        return features

    def _get_recent_games(
        self,
        player_id: int,
        as_of_date: date,
        days: int = 30
    ) -> pd.DataFrame:
        """Fetch recent games as DataFrame."""
        start_date = as_of_date - timedelta(days=days)

        stats = self.db.query(PlayerGameStats).filter(
            PlayerGameStats.player_id == player_id,
            PlayerGameStats.game_date >= start_date,
            PlayerGameStats.game_date < as_of_date
        ).order_by(PlayerGameStats.game_date.asc()).all()

        if not stats:
            return pd.DataFrame()

        records = []
        for s in stats:
            records.append({
                "game_date": s.game_date,
                "minutes": s.minutes or 0,
                "points": s.points or 0,
                "rebounds": s.rebounds or 0,
                "assists": s.assists or 0,
                "steals": s.steals or 0,
                "blocks": s.blocks or 0,
                "turnovers": s.turnovers or 0,
                "field_goals_attempted": s.field_goals_attempted or 0,
                "fantasy_points": s.fantasy_points or 0,
            })

        return pd.DataFrame(records)
