from celery_worker import celery_app
from app.utils.slack import send_slack_message

@celery_app.task(name="app.tasks.slack_tasks.send_slack_reply")
def send_slack_reply(channel, text, thread_ts=None):
    print(f"[Celery] Sending Slack message to {channel}, thread {thread_ts}")
    send_slack_message(channel, text, thread_ts)
