import os
import secrets
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
import httpx
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from app.auth.auth import create_access_token, create_refresh_token
from app.auth.utils import get_password_hash

router = APIRouter()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
COOKIE_MAX_AGE = 60 * 60 * 24 * 30


@router.get("/auth/github")
def github_login():
    if not GITHUB_CLIENT_ID:
        from fastapi import HTTPException
        raise HTTPException(503, "GitHub OAuth not configured")
    return RedirectResponse(
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}&scope=user:email"
    )


@router.get("/auth/github/callback")
async def github_callback(code: str, db: Session = Depends(get_db)):
    async with httpx.AsyncClient(timeout=10) as client:
        tr = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        gh_token = tr.json().get("access_token")
        if not gh_token:
            return RedirectResponse(f"{FRONTEND_URL}/login?error=github_auth_failed")

        ur = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {gh_token}"},
        )
        gh_user = ur.json()

        er = await client.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"Bearer {gh_token}"},
        )
        emails = er.json() if isinstance(er.json(), list) else []

    github_id = str(gh_user["id"])
    username = gh_user.get("login", f"user_{github_id}")
    primary_email = next(
        (e["email"] for e in emails if e.get("primary") and e.get("verified")),
        f"{username}@users.noreply.github.com",
    )

    user = db.query(User).filter(User.github_id == github_id).first()
    if not user:
        user = db.query(User).filter(User.email == primary_email).first()
    if not user:
        user = User(
            username=username,
            email=primary_email,
            hashed_password=get_password_hash(secrets.token_hex(32)),
            role="developer",
            github_id=github_id,
        )
        db.add(user)
    else:
        user.github_id = github_id

    db.commit()
    db.refresh(user)

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id), "role": user.role})

    response = RedirectResponse(f"{FRONTEND_URL}/auth/callback?token={access_token}")
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
    )
    return response
