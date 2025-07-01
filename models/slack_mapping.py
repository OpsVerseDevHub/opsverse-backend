from sqlalchemy import Column, Integer, String
from database import Base

class SlackProjectMap(Base):
    __tablename__ = "slack_project_map"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)
    slack_channel_id = Column(String, nullable=False)
