from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.schemas.user import UserCreate, UserResponse
from models.user import User
from app.crud import user as user_crud
from database import get_db
from app.auth.dependencies import require_role, get_current_user

router = APIRouter()


@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # First user ever gets admin role regardless of what was sent
        is_first = db.query(User).count() == 0
        if is_first:
            user = user.model_copy(update={"role": "admin"})
        return user_crud.create_user(db, user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username or email already taken")


@router.get("/users", response_model=List[UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    return user_crud.get_users(db, skip, limit)


@router.get("/users/me", response_model=UserResponse)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


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
