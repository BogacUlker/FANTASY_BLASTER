"""
Celery application configuration.
"""
from celery import Celery
from app.config import settings

celery_app = Celery(
    "fantasy_bball",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.data_ingestion",
        "app.tasks.predictions",
        "app.tasks.notifications",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=86400,  # Results expire after 24 hours
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "fetch-daily-games": {
        "task": "app.tasks.data_ingestion.fetch_daily_games",
        "schedule": 3600.0,  # Every hour
    },
    "update-player-stats": {
        "task": "app.tasks.data_ingestion.update_player_stats",
        "schedule": 1800.0,  # Every 30 minutes during games
    },
    "generate-daily-predictions": {
        "task": "app.tasks.predictions.generate_daily_predictions",
        "schedule": 21600.0,  # Every 6 hours
    },
    "cleanup-old-predictions": {
        "task": "app.tasks.predictions.cleanup_old_predictions",
        "schedule": 86400.0,  # Daily
    },
}
