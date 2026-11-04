from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    project_id: int
    status: str = "todo"
    priority: str = "medium"
    due_date: Optional[date] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[int] = None
    project_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None


class TaskStatusUpdate(BaseModel):
    status: str


class Task(TaskBase):
    id: int
    github_issue_id: Optional[int] = None
    commit_hash: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
