"""
Data ingestion tasks for fetching NBA data.

Celery tasks for syncing teams, players, and game stats from NBA API.
"""
import logging
from datetime import date, datetime, timedelta

from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.services.nba.client import NBAApiClient
from app.services.nba.sync import NBASyncService
from app.services.nba.boxscore import BoxScoreService

logger = logging.getLogger(__name__)


def get_db_session():
    """Create a database session for task execution."""
    return SessionLocal()


@celery_app.task(bind=True, max_retries=3)
def fetch_daily_games(self, game_date: str | None = None):
    """
    Fetch and ingest all games for a specific date.

    Args:
        game_date: Date string in YYYY-MM-DD format. Defaults to today.
    """
    db = get_db_session()
    try:
        if game_date:
            target_date = datetime.strptime(game_date, "%Y-%m-%d").date()
        else:
            target_date = date.today()

        logger.info(f"Fetching games for {target_date}")

        boxscore_service = BoxScoreService(db)
        result = boxscore_service.ingest_games_for_date(target_date)

        logger.info(f"Games ingestion complete: {result}")

        return {
            "status": "success",
            "date": target_date.isoformat(),
            "games_processed": result["games_processed"],
            "stats_created": result["stats_created"],
            "stats_updated": result["stats_updated"],
        }
    except Exception as exc:
        logger.error(f"Failed to fetch games: {exc}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def update_player_stats(self, player_id: int | None = None):
    """
    Update player statistics from recent games.

    Args:
        player_id: Specific player ID to update, or None for yesterday's games.
    """
    db = get_db_session()
    try:
        if player_id:
            logger.info(f"Updating stats for player {player_id}")
            boxscore_service = BoxScoreService(db)
            result = boxscore_service.backfill_player_history(
                player_id,
                seasons=[NBAApiClient.CURRENT_SEASON]
            )
        else:
            # Update yesterday's games by default
            yesterday = date.today() - timedelta(days=1)
            logger.info(f"Updating stats for {yesterday}")
            boxscore_service = BoxScoreService(db)
            result = boxscore_service.ingest_games_for_date(yesterday)

        return {"status": "success", "result": result}
    except Exception as exc:
        logger.error(f"Failed to update player stats: {exc}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def sync_nba_teams(self):
    """
    Synchronize all NBA teams to the database.
    """
    db = get_db_session()
    try:
        logger.info("Syncing NBA teams")

        sync_service = NBASyncService(db)
        result = sync_service.sync_all_teams()

        logger.info(f"Team sync complete: {result}")

        return {
            "status": "success",
            "created": result["created"],
            "updated": result["updated"],
        }
    except Exception as exc:
        logger.error(f"Failed to sync teams: {exc}")
        raise self.retry(exc=exc, countdown=300)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def sync_nba_players(self, season: str | None = None):
    """
    Synchronize all active NBA players for a season.

    Args:
        season: Season string (e.g., "2024-25"). Defaults to current.
    """
    db = get_db_session()
    try:
        logger.info(f"Syncing NBA players for season {season or 'current'}")

        sync_service = NBASyncService(db)
        result = sync_service.sync_all_players(season)

        logger.info(f"Player sync complete: {result}")

        return {
            "status": "success",
            "created": result["created"],
            "updated": result["updated"],
            "skipped": result["skipped"],
        }
    except Exception as exc:
        logger.error(f"Failed to sync players: {exc}")
        raise self.retry(exc=exc, countdown=300)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def sync_team_roster(self, team_id: int, season: str | None = None):
    """
    Synchronize roster for a specific team.

    Args:
        team_id: Database team ID.
        season: Season string. Defaults to current.
    """
    db = get_db_session()
    try:
        logger.info(f"Syncing roster for team {team_id}")

        sync_service = NBASyncService(db)
        result = sync_service.sync_team_roster(team_id, season)

        return {"status": "success", "synced": result["synced"]}
    except Exception as exc:
        logger.error(f"Failed to sync roster: {exc}")
        raise self.retry(exc=exc, countdown=120)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def sync_nba_rosters(self):
    """
    Synchronize all NBA team rosters.
    """
    db = get_db_session()
    try:
        from app.models.team import Team

        logger.info("Syncing all NBA rosters")

        teams = db.query(Team).all()
        sync_service = NBASyncService(db)

        total_synced = 0
        errors = 0

        for team in teams:
            try:
                result = sync_service.sync_team_roster(team.id)
                total_synced += result["synced"]
            except Exception as e:
                logger.warning(f"Failed to sync roster for {team.name}: {e}")
                errors += 1

        return {
            "status": "success",
            "teams_processed": len(teams),
            "players_synced": total_synced,
            "errors": errors,
        }
    except Exception as exc:
        logger.error(f"Failed to sync rosters: {exc}")
        raise self.retry(exc=exc, countdown=300)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=2)
def backfill_historical_data(
    self,
    start_date: str | None = None,
    end_date: str | None = None,
    seasons: list[str] | None = None,
):
    """
    Backfill historical game data.

    Args:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        seasons: List of seasons to backfill (e.g., ["2022-23", "2023-24"]).
    """
    db = get_db_session()
    try:
        boxscore_service = BoxScoreService(db)

        if start_date and end_date:
            # Date range backfill
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()

            logger.info(f"Backfilling data from {start} to {end}")
            result = boxscore_service.backfill_date_range(start, end)

        elif seasons:
            # Season-based backfill
            logger.info(f"Backfilling seasons: {seasons}")

            # For season backfill, we need to iterate through each day
            total_result = {
                "games_processed": 0,
                "stats_created": 0,
                "stats_updated": 0,
                "errors": 0,
            }

            for season in seasons:
                # Parse season to date range
                start_year = int(season.split("-")[0])
                season_start = date(start_year, 10, 1)  # Season starts ~Oct
                season_end = date(start_year + 1, 6, 30)  # Season ends ~June

                result = boxscore_service.backfill_date_range(season_start, season_end)

                for key in total_result:
                    total_result[key] += result.get(key, 0)

            result = total_result

        else:
            # Default: last 7 days
            end = date.today()
            start = end - timedelta(days=7)

            logger.info(f"Backfilling last 7 days: {start} to {end}")
            result = boxscore_service.backfill_date_range(start, end)

        logger.info(f"Backfill complete: {result}")

        return {"status": "success", **result}
    except Exception as exc:
        logger.error(f"Failed to backfill data: {exc}")
        raise self.retry(exc=exc, countdown=600)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def fetch_injury_report(self):
    """
    Fetch and update player injury statuses.

    Note: NBA API doesn't provide direct injury endpoints.
    This task would need to scrape or use a third-party injury feed.
    """
    db = get_db_session()
    try:
        logger.info("Fetching injury report")

        # Injury data would typically come from:
        # 1. NBA official injury report (scraping required)
        # 2. Third-party sports data providers
        # 3. News aggregation services

        # For now, log that this needs external implementation
        logger.warning(
            "Injury report fetching requires external data source. "
            "Consider integrating with a sports data provider."
        )

        return {
            "status": "pending_implementation",
            "message": "Injury data requires external API integration",
        }
    except Exception as exc:
        logger.error(f"Failed to fetch injury report: {exc}")
        raise self.retry(exc=exc, countdown=120)
    finally:
        db.close()


@celery_app.task
def run_data_quality_check():
    """
    Run data quality checks on the database.
    """
    db = get_db_session()
    try:
        from app.services.nba.validators import DataQualityChecker

        logger.info("Running data quality checks")

        checker = DataQualityChecker(db)
        results = checker.run_quality_checks()

        logger.info(f"Quality check complete: {results['summary']}")

        return results
    except Exception as exc:
        logger.error(f"Failed to run quality check: {exc}")
        return {"status": "error", "message": str(exc)}
    finally:
        db.close()


@celery_app.task
def full_sync():
    """
    Run a full data sync: teams, players, and recent games.

    This is useful for initial setup or recovery.
    """
    logger.info("Starting full sync")

    # Chain the sync tasks
    sync_nba_teams.delay()
    sync_nba_players.delay()
    sync_nba_rosters.delay()

    # Backfill last 30 days
    end = date.today()
    start = end - timedelta(days=30)
    backfill_historical_data.delay(
        start_date=start.isoformat(),
        end_date=end.isoformat()
    )

    return {"status": "sync_tasks_queued"}
