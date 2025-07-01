from celery_worker import celery_app
from app.utils.slack import send_slack_message

@celery_app.task(name="app.tasks.slack_tasks.send_slack_reply")
def send_slack_reply(channel, text, thread_ts=None):
    print("Celery Executing send_slack_reply")
    send_slack_message(channel, text, thread_ts)
    print("slack message sent (sync executed)")

# app/services/slack_service.py
from app.tasks.slack_tasks import send_slack_reply

def notify_channel_about_event(event_data):
    event = event_data.get("event", {})
    channel = event.get("channel")
    text = event.get("text")
    ts = event.get("ts")
    user = event.get("user")

    if channel and text and user:
        reply = f":robot_face: Hi <@{user}>, got your message!\n> {text}"
        send_slack_reply.delay(channel, reply, ts)