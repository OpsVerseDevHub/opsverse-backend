from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    owner_id: Optional[int] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class Project(ProjectBase):
    id: int
    status: str
    owner_id: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
