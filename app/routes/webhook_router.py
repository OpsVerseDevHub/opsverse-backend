from fastapi import APIRouter, Header, Request, HTTPException, Depends, Query
import hmac
import hashlib
import json
import os
from dotenv import load_dotenv
from app.webhooks.dispatcher import dispatch_event
from app.schemas.github_events import GitHubEventLogOut
from app.crud import github_event as github_event_crud
from database import get_db
from sqlalchemy.orm import Session
from models.github_event import GitHubEvent
from datetime import datetime
from typing import Optional, List
from app.auth.dependencies import require_role
from app.websocket.manager import manager
from models.user import User

load_dotenv()

router = APIRouter()


def _get_github_secret() -> str:
    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    if not secret:
        raise HTTPException(status_code=503, detail="GitHub webhook not configured")
    return secret


def _parse_event(event: GitHubEvent) -> dict:
    try:
        payload = json.loads(event.payload)
    except Exception:
        payload = {}

    summary: dict = {}
    if event.event_type == "push":
        summary = {
            "pusher": payload.get("pusher", {}).get("name"),
            "ref": payload.get("ref", ""),
            "repo": payload.get("repository", {}).get("full_name"),
            "commits": [
                {
                    "hash": c.get("id", "")[:7],
                    "message": c.get("message", "").split("\n")[0],
                    "url": c.get("url"),
                }
                for c in payload.get("commits", [])[:5]
            ],
        }
    elif event.event_type == "pull_request":
        pr = payload.get("pull_request", {})
        summary = {
            "action": payload.get("action"),
            "number": payload.get("number"),
            "title": pr.get("title"),
            "user": payload.get("sender", {}).get("login"),
            "repo": payload.get("repository", {}).get("full_name"),
            "url": pr.get("html_url"),
        }
    elif event.event_type == "issues":
        issue = payload.get("issue", {})
        summary = {
            "action": payload.get("action"),
            "number": issue.get("number"),
            "title": issue.get("title"),
            "user": payload.get("sender", {}).get("login"),
            "repo": payload.get("repository", {}).get("full_name"),
            "url": issue.get("html_url"),
        }

    return {
        "id": event.id,
        "event_type": event.event_type,
        "received_at": event.received_at.isoformat() if event.received_at else None,
        "summary": summary,
    }


@router.post("/webhooks/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(...),
    x_hub_signature_256: str = Header(None),
    db: Session = Depends(get_db),
):
    body = await request.body()

    if x_hub_signature_256:
        secret = _get_github_secret()
        expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, x_hub_signature_256):
            raise HTTPException(status_code=400, detail="Invalid signature")

    payload = await request.json()
    await dispatch_event(x_github_event, payload, db)
    repo = payload.get("repository", {}).get("full_name", "unknown")
    await manager.broadcast({"type": "github_event", "event_type": x_github_event, "repo": repo})
    return {"message": "Webhook received"}


@router.get("/webhooks/logs", response_model=List[GitHubEventLogOut])
def get_logs(
    event_type: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    delivery_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return github_event_crud.get_filtered_events(
        db,
        event_type=event_type,
        from_date=from_date,
        to_date=to_date,
        delivery_id=delivery_id,
    )


@router.get("/github/activity")
def get_activity(
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin", "manager", "developer")),
):
    events = (
        db.query(GitHubEvent)
        .order_by(GitHubEvent.received_at.desc())
        .limit(limit)
        .all()
    )
    return [_parse_event(e) for e in events]
