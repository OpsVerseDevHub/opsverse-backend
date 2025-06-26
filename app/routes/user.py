from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.user import UserCreate, UserResponse
from models.user import User
from app.crud import user as user_crud
from database import get_db
from app.auth.dependencies import require_role

router = APIRouter()


@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_crud.create_user(db, user)


@router.get("/users", response_model=List[UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    return user_crud.get_users(db, skip, limit)


@router.get("/users/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "developer")),
):
    # Allow users to see their own profile, or admin can see any
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return user_crud.get_user(db, user_id)
