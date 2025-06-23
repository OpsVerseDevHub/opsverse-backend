from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from models.user import User
from app.schemas.user import UserCreate, UserRead
from app.dependencies import get_db

router = APIRouter()

@router.get("/users", response_model=list[UserRead])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.username = user.username
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}
