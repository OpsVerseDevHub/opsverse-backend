from app.tasks.slack_tasks import send_slack_reply
from models.slack_mapping import SlackProjectMap  
from database import SessionLocal  
from app.tasks.slack_tasks import send_slack_reply  

def get_slack_channel_for_project(project_id: int) -> str:  
    db = SessionLocal()  
    record = db.query(SlackProjectMap).filter(SlackProjectMap.project_id == project_id).first()  
    db.close()  
    return record.slack_channel_id if record else None  

def notify_project_channel(project_id: int, message: str, thread_ts=None):  
    channel = get_slack_channel_for_project(project_id)  
    if channel:  
        send_slack_reply.delay(channel, message, thread_ts)  


def notify_channel_about_event(event_data: dict):
    print("Slack event triggered for Celery")
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
        # Send to Celery for async processing
        print("Dispatching Celery task")
        send_slack_reply.delay(channel, reply_text, ts)

