from app.tasks.slack_tasks import send_slack_reply
from models.slack_mapping import SlackProjectMap
from sqlalchemy.orm import Session
from app.crud import slack_crud
from database import get_db

def get_slack_channel_for_project(project_id: int) -> str:
    db = next(get_db())
    record = db.query(SlackProjectMap).filter(SlackProjectMap.project_id == project_id).first()
    db.close()
    return record.slack_channel_id if record else None

def notify_project_channel(project_id: int, message: str, thread_ts=None):
    channel = get_slack_channel_for_project(project_id)
    if channel:
        send_slack_reply.delay(channel, message, thread_ts)

def notify_channel_about_event(event_data: dict):
    event = event_data.get("event", {})
    user = event.get("user")
    text = event.get("text")
    channel = event.get("channel")
    ts = event.get("ts")

    if user and text and channel:
        reply_text = (
            f":robot_face: Hey <@{user}>! I received your message:\n"
            f"> {text}\n\n"
            f"_If this message is related to a task or project, please reply with details!_"
        )
        send_slack_reply.delay(channel, reply_text, ts)

        db = next(get_db())
        slack_crud.save_slack_message(db, user, channel, text, ts)

def reply_to_slack_thread(project_id: int, message_text: str):
    db = next(get_db())
    mapping = slack_crud.get_mapping_by_project(db, project_id)
    if mapping and mapping.slack_channel_id:
        thread_ts = slack_crud.get_latest_thread_ts(db, mapping.slack_channel_id)
        if thread_ts:
            send_slack_reply.delay(mapping.slack_channel_id, message_text, thread_ts)
