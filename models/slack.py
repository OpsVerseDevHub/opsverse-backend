from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from database import Base
from datetime import datetime

class SlackMessage(Base):
    __tablename__ = "slack_messages"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String)
    channel_id = Column(String)
    text = Column(String)
    timestamp = Column(String)
    received_at = Column(DateTime, default=datetime.utcnow)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)