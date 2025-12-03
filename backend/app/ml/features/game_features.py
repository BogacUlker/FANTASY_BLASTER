"""
Game context feature builders.

Handles game-level features including opponent, schedule, and situational factors.
"""
import logging
from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.team import Team
from app.models.game_stats import PlayerGameStats
from app.models.player import Player

logger = logging.getLogger(__name__)


class GameContextFeatureBuilder:
    """
    Builder for game context features.

    Handles opponent analysis, schedule factors, and situational context.
    """

    # NBA team defensive tiers (simplified - would be updated dynamically)
    DEFAULT_DEF_RATING = 112.0  # League average

    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self._team_stats_cache: dict[int, dict] = {}

    def build_opponent_features(
        self,
        opponent_team_id: int,
        player_position: str | None = None,
        as_of_date: date | None = None
    ) -> dict[str, float]:
        """
        Build opponent strength features.

        Args:
            opponent_team_id: Database team ID.
            player_position: Player's position for matchup.
            as_of_date: Reference date.

        Returns:
            Dictionary of opponent features.
        """
        features = {}

        # Get opponent team stats
        opp_stats = self._get_team_defensive_stats(opponent_team_id, as_of_date)

        features["opp_def_rating"] = opp_stats.get("def_rating", self.DEFAULT_DEF_RATING)
        features["opp_pace"] = opp_stats.get("pace", 100.0)

        # Opponent allows fantasy points
        features["opp_fp_allowed"] = opp_stats.get("fp_allowed_avg", 45.0)

        # Position-specific opponent features
        if player_position:
            pos_allowed = opp_stats.get(f"fp_allowed_{player_position.lower()}", 45.0)
            features["opp_fp_allowed_position"] = pos_allowed

        # Relative to league average
        features["opp_def_vs_avg"] = features["opp_def_rating"] - self.DEFAULT_DEF_RATING

        return features

    def build_pace_features(
        self,
        player_team_id: int,
        opponent_team_id: int
    ) -> dict[str, float]:
        """
        Build pace and tempo features.

        Args:
            player_team_id: Player's team ID.
            opponent_team_id: Opponent team ID.

        Returns:
            Dictionary of pace features.
        """
        features = {}

        # Get team paces
        player_team_stats = self._get_team_defensive_stats(player_team_id)
        opp_team_stats = self._get_team_defensive_stats(opponent_team_id)

        player_pace = player_team_stats.get("pace", 100.0)
        opp_pace = opp_team_stats.get("pace", 100.0)

        # Expected game pace
        features["expected_pace"] = (player_pace + opp_pace) / 2

        # Pace deviation from average
        features["pace_vs_avg"] = features["expected_pace"] - 100.0

        # High pace indicator
        features["is_high_pace_game"] = features["expected_pace"] > 102.0

        return features

    def build_rest_advantage_features(
        self,
        player_team_id: int,
        opponent_team_id: int,
        game_date: date
    ) -> dict[str, float]:
        """
        Build rest advantage features.

        Args:
            player_team_id: Player's team ID.
            opponent_team_id: Opponent team ID.
            game_date: Game date.

        Returns:
            Dictionary of rest features.
        """
        features = {}

        # Get days since last game for each team
        player_team_rest = self._get_team_rest_days(player_team_id, game_date)
        opp_team_rest = self._get_team_rest_days(opponent_team_id, game_date)

        features["team_rest_days"] = player_team_rest
        features["opp_rest_days"] = opp_team_rest
        features["rest_advantage"] = player_team_rest - opp_team_rest

        # Fatigue indicators
        features["team_b2b"] = player_team_rest == 1
        features["opp_b2b"] = opp_team_rest == 1

        return features

    def build_schedule_density_features(
        self,
        player_team_id: int,
        game_date: date
    ) -> dict[str, float]:
        """
        Build schedule density features.

        Args:
            player_team_id: Team ID.
            game_date: Game date.

        Returns:
            Dictionary of schedule features.
        """
        features = {}

        # Games in last 7 days
        week_ago = game_date - timedelta(days=7)
        games_last_week = self._count_team_games(player_team_id, week_ago, game_date)

        features["team_games_last_7d"] = games_last_week

        # Dense schedule indicator (4+ games in week)
        features["dense_schedule"] = games_last_week >= 4

        # Games coming up (would need schedule data)
        features["games_next_3d"] = 0  # Placeholder

        return features

    def build_time_context_features(self, game_date: date) -> dict[str, Any]:
        """
        Build temporal context features.

        Args:
            game_date: Game date.

        Returns:
            Dictionary of time features.
        """
        features = {}

        # Day of week encoding
        features["dow_monday"] = game_date.weekday() == 0
        features["dow_tuesday"] = game_date.weekday() == 1
        features["dow_wednesday"] = game_date.weekday() == 2
        features["dow_thursday"] = game_date.weekday() == 3
        features["dow_friday"] = game_date.weekday() == 4
        features["dow_saturday"] = game_date.weekday() == 5
        features["dow_sunday"] = game_date.weekday() == 6

        # Weekend indicator
        features["is_weekend"] = game_date.weekday() >= 5

        # Month encoding
        features["month"] = game_date.month

        # Season phase
        if game_date.month in [10, 11]:
            features["season_phase_early"] = True
            features["season_phase_mid"] = False
            features["season_phase_late"] = False
        elif game_date.month in [12, 1, 2]:
            features["season_phase_early"] = False
            features["season_phase_mid"] = True
            features["season_phase_late"] = False
        else:
            features["season_phase_early"] = False
            features["season_phase_mid"] = False
            features["season_phase_late"] = True

        return features

    def _get_team_defensive_stats(
        self,
        team_id: int,
        as_of_date: date | None = None
    ) -> dict[str, float]:
        """Get team's defensive stats (cached)."""
        if team_id in self._team_stats_cache:
            return self._team_stats_cache[team_id]

        # Calculate from game data
        stats = self._calculate_team_def_stats(team_id, as_of_date)
        self._team_stats_cache[team_id] = stats

        return stats

    def _calculate_team_def_stats(
        self,
        team_id: int,
        as_of_date: date | None = None
    ) -> dict[str, float]:
        """Calculate team defensive statistics from games."""
        # This would aggregate opponent scoring against this team
        # For now, return defaults

        return {
            "def_rating": self.DEFAULT_DEF_RATING,
            "pace": 100.0,
            "fp_allowed_avg": 45.0,
            "fp_allowed_pg": 45.0,
            "fp_allowed_sg": 40.0,
            "fp_allowed_sf": 38.0,
            "fp_allowed_pf": 40.0,
            "fp_allowed_c": 42.0,
        }

    def _get_team_rest_days(self, team_id: int, game_date: date) -> int:
        """Get days since team's last game."""
        # Get team's players
        players = self.db.query(Player.id).filter(Player.team_id == team_id).all()
        player_ids = [p.id for p in players]

        if not player_ids:
            return 3  # Default rest

        # Find most recent game
        last_game = self.db.query(func.max(PlayerGameStats.game_date)).filter(
            PlayerGameStats.player_id.in_(player_ids),
            PlayerGameStats.game_date < game_date
        ).scalar()

        if last_game:
            return (game_date - last_game).days
        return 3  # Default

    def _count_team_games(
        self,
        team_id: int,
        start_date: date,
        end_date: date
    ) -> int:
        """Count team games in date range."""
        players = self.db.query(Player.id).filter(Player.team_id == team_id).all()
        player_ids = [p.id for p in players]

        if not player_ids:
            return 0

        # Count distinct game dates
        games = self.db.query(
            func.count(func.distinct(PlayerGameStats.game_date))
        ).filter(
            PlayerGameStats.player_id.in_(player_ids),
            PlayerGameStats.game_date >= start_date,
            PlayerGameStats.game_date < end_date
        ).scalar()

        return games or 0


class VegasFeatureBuilder:
    """
    Builder for Vegas/betting line features.

    Would integrate with odds APIs for:
    - Over/under totals
    - Spread indicators
    - Player props
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def build_vegas_features(
        self,
        player_id: int,
        game_date: date
    ) -> dict[str, float]:
        """
        Build Vegas-based features (placeholder).

        Would require external betting data API.
        """
        features = {}

        # Placeholders - would be populated from odds API
        features["game_total"] = 225.0  # Over/under
        features["spread"] = 0.0  # Point spread
        features["implied_team_total"] = 112.5

        # Player props (if available)
        features["pts_prop"] = 0.0
        features["reb_prop"] = 0.0
        features["ast_prop"] = 0.0

        return features
