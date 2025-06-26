from pydantic import BaseModel
from datetime import datetime


class GitHubEventLogOut(BaseModel):
    id: int
    event_type: str
    delivery_id: str
    payload: str
    received_at: datetime

    class Config:
        from_attributes = True
