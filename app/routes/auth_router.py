from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from app.auth.utils import verify_password
from app.auth.auth import create_access_token, create_refresh_token, SECRET_KEY, ALGORITHM
from database import get_db
from models.user import User

router = APIRouter()

REFRESH_COOKIE = "refresh_token"
COOKIE_MAX_AGE = 60 * 60 * 24 * 30


@router.post("/token")
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id), "role": user.role})

    response.set_cookie(
        key=REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/auth/refresh")
def refresh_access_token(request: Request):
    token = request.cookies.get(REFRESH_COOKIE)
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id: str = payload.get("sub")
        role: str = payload.get("role", "developer")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access_token = create_access_token({"sub": user_id, "role": role})
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie(REFRESH_COOKIE)
    return {"message": "Logged out"}
