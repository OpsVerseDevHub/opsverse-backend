from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "opsverse",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND")
)

celery_app.conf.task_routes = {
    "app.tasks.slack_tasks.send_slack_reply": {"queue": "slack"}
}

from app.tasks import slack_tasks