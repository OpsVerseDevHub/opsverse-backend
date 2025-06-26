from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.crud import task as task_crud
from database import get_db
from app.auth.dependencies import require_role
from models.user import User

router = APIRouter()


@router.post("/tasks", response_model=Task)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager")),
):
    return task_crud.create_task(db, task)


@router.get("/tasks", response_model=List[Task])
def read_tasks(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "developer")),
):
    if current_user.role == "developer":
        return (
            db.query(Task)
            .filter(Task.assignee_id == current_user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    return task_crud.get_tasks(db, skip, limit)


@router.get("/tasks/{task_id}", response_model=Task)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "developer")),
):
    task = task_crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager")),
):
    return task_crud.update_task(db, task_id, task)


@router.delete("/tasks/{task_id}", response_model=Task)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager")),
):
    return task_crud.delete_task(db, task_id)
