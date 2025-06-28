from models.slack import SlackMessage
from database import get_db
from app.schemas.slack import SlackMessageCreate

def create_slack_message(db, message_data: SlackMessageCreate):
    msg = SlackMessage(**message_data.dict())
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

