from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.project import ProjectCreate, Project
from app.crud import project as project_crud
from database import get_db
from app.auth.dependencies import require_role
from models.user import User

router = APIRouter()

@router.post("/projects", response_model=Project)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    return project_crud.create_project(db, project)

@router.get("/projects", response_model=List[Project])
def read_projects(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "developer"))
):
    return project_crud.get_projects(db, skip, limit)

@router.get("/projects/{project_id}", response_model=Project)
def read_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "developer"))
):
    return project_crud.get_project(db, project_id)

@router.put("/projects/{project_id}", response_model=Project)
def update_project(
    project_id: int,
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    return project_crud.update_project(db, project_id, project)

@router.delete("/projects/{project_id}", response_model=Project)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager"))
):
    return project_crud.delete_project(db, project_id)
