from celery import Celery
from celery.schedules import crontab
from app.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

# Initialize Celery app
celery_app = Celery(
    "packers_hub",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks.periodic_tasks"]
)

# Celery Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Chicago",  # Green Bay timezone
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)

# Celery Beat Schedule for Periodic Tasks
celery_app.conf.beat_schedule = {
    "update-packers-roster-weekly": {
        "task": "app.tasks.periodic_tasks.update_packers_roster",
        "schedule": crontab(day_of_week=1, hour=2, minute=0),  # Every Monday at 2 AM
    },
}

if __name__ == "__main__":
    celery_app.start()
