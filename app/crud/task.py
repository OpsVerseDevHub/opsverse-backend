from sqlalchemy.orm import Session
from models.task import Task
from app.schemas.task import TaskCreate
from app.schemas.task import TaskUpdate
from models.user import User
from models.project import Project
from fastapi import HTTPException


def create_task(db: Session, task: TaskCreate):
    # Validate assignee
    assignee = db.query(User).filter(User.id == task.assignee_id).first()
    if not assignee:
        raise HTTPException(status_code=400, detail="Assignee does not exist")

    # Validate project
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=400, detail="Project does not exist")

    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_tasks(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Task).offset(skip).limit(limit).all()


def get_task(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()


def update_task(db: Session, task_id: int, updated_task: TaskUpdate):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Optional validations
    if updated_task.assignee_id:
        assignee = db.query(User).filter(User.id == updated_task.assignee_id).first()
        if not assignee:
            raise HTTPException(status_code=400, detail="Assignee does not exist")
    if updated_task.project_id:
        project = (
            db.query(Project).filter(Project.id == updated_task.project_id).first()
        )
        if not project:
            raise HTTPException(status_code=400, detail="Project does not exist")

    for attr, value in updated_task.dict(exclude_unset=True).items():
        setattr(task, attr, value)

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        return None
    db.delete(db_task)
    db.commit()
    return db_task


def update_task_with_commit(db: Session, commit_message: str, commit_hash: str):
    """
    Update task if commit message contains reference to task (e.g. TASK-123)
    """
    # Example logic: assume commit message contains TASK-<id>
    import re

    match = re.search(r"TASK-(\d+)", commit_message)
    if not match:
        return None  # No task ref found

    task_id = int(match.group(1))

    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return None  # Task not found

    # Prevent duplicate commit processing (idempotency)
    if task.commit_hash == commit_hash:
        return task  # Already synced

    task.commit_hash = commit_hash
    task.status = "in_progress"  # or "done", based on business rule
    db.commit()
    db.refresh(task)

    return task


def update_task_status(db: Session, task_id: int, status: str):
    """
    Update task status manually or via issue-based event
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = status
        db.commit()
        db.refresh(task)
    return task
