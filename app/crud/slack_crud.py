from models.slack import SlackMessage
from database import get_db
from app.schemas.slack import SlackMessageCreate
from sqlalchemy.orm import session

def create_slack_message(db: session, message_data: SlackMessageCreate):
    existing = db.query(SlackMessage).filter(SlackMessage.id == message_data.id).first()
    if existing:
        return existing  # or just return None
    db_msg = SlackMessage(**message_data.dict())
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return db_msg


