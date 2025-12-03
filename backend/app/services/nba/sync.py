"""
NBA data synchronization service.

Handles syncing teams, players, and rosters from NBA API to database.
"""
import logging
from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.team import Team
from app.models.player import Player, InjuryStatus
from app.services.nba.client import NBAApiClient

logger = logging.getLogger(__name__)


class NBASyncService:
    """
    Service for synchronizing NBA data to the database.

    Handles teams, players, and roster relationships.
    """

    def __init__(self, db: Session, nba_client: NBAApiClient | None = None):
        self.db = db
        self.nba_client = nba_client or NBAApiClient()
        self.logger = logging.getLogger(__name__)

    def sync_all_teams(self) -> dict[str, int]:
        """
        Sync all NBA teams to the database.

        Returns:
            Dict with counts of created and updated teams.
        """
        self.logger.info("Starting team sync")
        teams = self.nba_client.get_all_teams()

        created = 0
        updated = 0

        for team_data in teams:
            existing = self.db.query(Team).filter(
                Team.nba_team_id == str(team_data["id"])
            ).first()

            if existing:
                # Update existing team
                existing.name = team_data["full_name"]
                existing.abbreviation = team_data["abbreviation"]
                existing.city = team_data["city"]
                existing.updated_at = datetime.utcnow()
                updated += 1
            else:
                # Create new team
                team = Team(
                    nba_team_id=str(team_data["id"]),
                    name=team_data["full_name"],
                    abbreviation=team_data["abbreviation"],
                    city=team_data["city"],
                    conference=self._get_conference(team_data["abbreviation"]),
                    division=self._get_division(team_data["abbreviation"]),
                )
                self.db.add(team)
                created += 1

        self.db.commit()
        self.logger.info(f"Team sync complete: {created} created, {updated} updated")

        return {"created": created, "updated": updated}

    def sync_all_players(self, season: str | None = None) -> dict[str, int]:
        """
        Sync all active players for a season.

        Args:
            season: Season string. Defaults to current.

        Returns:
            Dict with counts of created and updated players.
        """
        self.logger.info(f"Starting player sync for season {season or 'current'}")
        players = self.nba_client.get_all_active_players(season)

        # Build team lookup
        team_lookup = {
            t.nba_team_id: t.id for t in self.db.query(Team).all()
        }

        created = 0
        updated = 0
        skipped = 0

        for player_data in players:
            try:
                result = self._sync_player(player_data, team_lookup)
                if result == "created":
                    created += 1
                elif result == "updated":
                    updated += 1
                else:
                    skipped += 1
            except Exception as e:
                self.logger.error(f"Failed to sync player {player_data.get('PERSON_ID')}: {e}")
                skipped += 1

        self.db.commit()
        self.logger.info(
            f"Player sync complete: {created} created, {updated} updated, {skipped} skipped"
        )

        return {"created": created, "updated": updated, "skipped": skipped}

    def _sync_player(
        self,
        player_data: dict[str, Any],
        team_lookup: dict[str, int]
    ) -> str:
        """
        Sync a single player.

        Returns:
            "created", "updated", or "skipped"
        """
        nba_player_id = str(player_data.get("PERSON_ID"))
        if not nba_player_id:
            return "skipped"

        existing = self.db.query(Player).filter(
            Player.nba_player_id == nba_player_id
        ).first()

        # Get team ID from lookup
        team_nba_id = str(player_data.get("TEAM_ID", ""))
        team_id = team_lookup.get(team_nba_id)

        # Parse player name
        full_name = player_data.get("DISPLAY_FIRST_LAST") or \
                    f"{player_data.get('PLAYER_FIRST_NAME', '')} {player_data.get('PLAYER_LAST_NAME', '')}".strip()

        if existing:
            # Update existing player
            existing.name = full_name
            existing.team_id = team_id
            existing.is_active = True
            existing.updated_at = datetime.utcnow()
            return "updated"
        else:
            # Create new player
            player = Player(
                nba_player_id=nba_player_id,
                name=full_name,
                team_id=team_id,
                is_active=True,
                injury_status=InjuryStatus.HEALTHY,
            )
            self.db.add(player)
            return "created"

    def sync_team_roster(self, team_id: int, season: str | None = None) -> dict[str, int]:
        """
        Sync roster for a specific team.

        Args:
            team_id: Database team ID.
            season: Season string. Defaults to current.

        Returns:
            Dict with counts of synced players.
        """
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise ValueError(f"Team {team_id} not found")

        self.logger.info(f"Syncing roster for {team.name}")
        roster = self.nba_client.get_team_roster(int(team.nba_team_id), season)

        synced = 0
        for player_data in roster:
            try:
                self._sync_roster_player(player_data, team.id)
                synced += 1
            except Exception as e:
                self.logger.error(f"Failed to sync roster player: {e}")

        self.db.commit()
        return {"synced": synced}

    def _sync_roster_player(self, player_data: dict[str, Any], team_id: int) -> None:
        """Sync a player from roster data."""
        nba_player_id = str(player_data.get("PLAYER_ID"))

        existing = self.db.query(Player).filter(
            Player.nba_player_id == nba_player_id
        ).first()

        if existing:
            # Update team and details
            existing.team_id = team_id
            existing.position = player_data.get("POSITION")
            existing.height = player_data.get("HEIGHT")
            existing.weight = self._parse_weight(player_data.get("WEIGHT"))
            existing.birth_date = self._parse_date(player_data.get("BIRTH_DATE"))
            existing.updated_at = datetime.utcnow()
        else:
            # Create new player from roster
            player = Player(
                nba_player_id=nba_player_id,
                name=player_data.get("PLAYER"),
                team_id=team_id,
                position=player_data.get("POSITION"),
                height=player_data.get("HEIGHT"),
                weight=self._parse_weight(player_data.get("WEIGHT")),
                birth_date=self._parse_date(player_data.get("BIRTH_DATE")),
                is_active=True,
                injury_status=InjuryStatus.HEALTHY,
            )
            self.db.add(player)

    def sync_player_details(self, player_id: int) -> bool:
        """
        Sync detailed info for a specific player.

        Args:
            player_id: Database player ID.

        Returns:
            True if successful.
        """
        player = self.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return False

        try:
            info = self.nba_client.get_player_info(int(player.nba_player_id))

            player.position = info.get("POSITION")
            player.height = info.get("HEIGHT")
            player.weight = self._parse_weight(info.get("WEIGHT"))
            player.birth_date = self._parse_date(info.get("BIRTHDATE"))
            player.headshot_url = self._build_headshot_url(player.nba_player_id)
            player.updated_at = datetime.utcnow()

            # Update team if changed
            team_nba_id = str(info.get("TEAM_ID", ""))
            if team_nba_id:
                team = self.db.query(Team).filter(
                    Team.nba_team_id == team_nba_id
                ).first()
                if team:
                    player.team_id = team.id

            self.db.commit()
            return True

        except Exception as e:
            self.logger.error(f"Failed to sync player details for {player_id}: {e}")
            return False

    def mark_inactive_players(self, active_player_ids: set[str]) -> int:
        """
        Mark players not in the active set as inactive.

        Args:
            active_player_ids: Set of NBA player IDs that are active.

        Returns:
            Count of players marked inactive.
        """
        count = 0
        players = self.db.query(Player).filter(Player.is_active == True).all()

        for player in players:
            if player.nba_player_id not in active_player_ids:
                player.is_active = False
                player.updated_at = datetime.utcnow()
                count += 1

        self.db.commit()
        return count

    @staticmethod
    def _parse_weight(weight_str: str | None) -> int | None:
        """Parse weight string to integer."""
        if not weight_str:
            return None
        try:
            return int(weight_str.replace(" lbs", "").strip())
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def _parse_date(date_str: str | None) -> date | None:
        """Parse date string to date object."""
        if not date_str:
            return None
        try:
            # NBA API uses various date formats
            for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%b %d, %Y"]:
                try:
                    return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
                except ValueError:
                    continue
            return None
        except Exception:
            return None

    @staticmethod
    def _build_headshot_url(nba_player_id: str) -> str:
        """Build CDN URL for player headshot."""
        return f"https://cdn.nba.com/headshots/nba/latest/1040x760/{nba_player_id}.png"

    @staticmethod
    def _get_conference(abbreviation: str) -> str:
        """Get conference for team abbreviation."""
        western = ["LAL", "LAC", "GSW", "PHX", "SAC", "DEN", "MIN", "OKC", "UTA", "POR",
                   "DAL", "HOU", "MEM", "NOP", "SAS"]
        return "Western" if abbreviation in western else "Eastern"

    @staticmethod
    def _get_division(abbreviation: str) -> str:
        """Get division for team abbreviation."""
        divisions = {
            "Atlantic": ["BOS", "BKN", "NYK", "PHI", "TOR"],
            "Central": ["CHI", "CLE", "DET", "IND", "MIL"],
            "Southeast": ["ATL", "CHA", "MIA", "ORL", "WAS"],
            "Northwest": ["DEN", "MIN", "OKC", "POR", "UTA"],
            "Pacific": ["GSW", "LAC", "LAL", "PHX", "SAC"],
            "Southwest": ["DAL", "HOU", "MEM", "NOP", "SAS"],
        }
        for division, teams in divisions.items():
            if abbreviation in teams:
                return division
        return "Unknown"
