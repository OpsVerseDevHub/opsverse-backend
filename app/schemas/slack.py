from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SlackMessageCreate(BaseModel):
    id: Optional[str] = None
    user_id: str
    channel_id: str
    text: str
    timestamp: str
    project_id: Optional[int] = None

class SlackMessageRead(SlackMessageCreate):
    received_at: Optional[datetime]
    
    class Config:
        orm_mode = True
