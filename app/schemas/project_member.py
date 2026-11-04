from pydantic import BaseModel
from datetime import datetime


class ProjectMemberCreate(BaseModel):
    project_id: int
    user_id: int
    role: str = "member"


class ProjectMemberResponse(ProjectMemberCreate):
    id: int
    joined_at: datetime

    class Config:
        from_attributes = True
