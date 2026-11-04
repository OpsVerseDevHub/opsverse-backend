from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.task import Task, TaskCreate, TaskUpdate, TaskStatusUpdate
from app.crud import task as task_crud
from database import get_db
from app.auth.dependencies import require_role
from app.websocket.manager import manager
from models.user import User
from models.task import Task as TaskModel
import asyncio

router = APIRouter()


def _broadcast(event: dict):
    try:
        asyncio.get_event_loop().create_task(manager.broadcast(event))
    except RuntimeError:
        pass


@router.post("/tasks", response_model=Task)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager")),
):
    created = await run_in_threadpool(task_crud.create_task, db, task)
    await manager.broadcast({"type": "task_created", "task_id": created.id, "project_id": created.project_id})
    return created


@router.get("/tasks", response_model=List[Task])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "developer")),
):
    query = db.query(TaskModel)
    if current_user.role == "developer":
        query = query.filter(TaskModel.assignee_id == current_user.id)
    if project_id is not None:
        query = query.filter(TaskModel.project_id == project_id)
    return query.offset(skip).limit(limit).all()


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
async def update_task(
    task_id: int,
    task: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager")),
):
    updated = await run_in_threadpool(task_crud.update_task, db, task_id, task)
    await manager.broadcast({"type": "task_updated", "task_id": task_id, "project_id": updated.project_id})
    return updated


@router.patch("/tasks/{task_id}/status", response_model=Task)
async def update_task_status(
    task_id: int,
    body: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "developer")),
):
    task = await run_in_threadpool(task_crud.update_task_status, db, task_id, body.status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await manager.broadcast({"type": "task_status_changed", "task_id": task_id, "project_id": task.project_id, "status": body.status})
    return task


@router.delete("/tasks/{task_id}", response_model=Task)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager")),
):
    task = await run_in_threadpool(task_crud.delete_task, db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await manager.broadcast({"type": "task_deleted", "task_id": task_id, "project_id": task.project_id})
    return task
