from models.slack import SlackMessage
from models.slack_mapping import SlackProjectMap
from sqlalchemy.orm import Session

def create_slack_message(db: Session, message_data):
    existing = db.query(SlackMessage).filter(SlackMessage.id == message_data.id).first()
    if existing:
        return existing
    msg = SlackMessage(**message_data.dict())
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def save_slack_message(db, user_id, channel_id, text, thread_ts):
    msg = SlackMessage(user_id=user_id, channel_id=channel_id, text=text, thread_ts=thread_ts)
    db.add(msg)
    db.commit()

def get_latest_thread_ts(db, channel_id: str):
    msg = db.query(SlackMessage).filter(SlackMessage.channel_id == channel_id).order_by(SlackMessage.created_at.desc()).first()
    return msg.thread_ts if msg else None

def get_mapping_by_project(db, project_id: int):
    return db.query(SlackProjectMap).filter(SlackProjectMap.project_id == project_id).first()
