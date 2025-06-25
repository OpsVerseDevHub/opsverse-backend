from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class GitHubEvent(Base):
    __tablename__ = "github_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)
    delivery_id = Column(String, unique=True, index=True)
    payload = Column(Text)  # Raw JSON string
    received_at = Column(DateTime(timezone=True), server_default=func.now())
