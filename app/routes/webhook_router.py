from fastapi import APIRouter, Header, Request, HTTPException, status, Depends, Query
import hmac
import hashlib
import os
from dotenv import load_dotenv
from app.webhooks.dispatcher import dispatch_event
from app.schemas.github_events import GitHubEventLogOut
from app.crud import github_event as github_event_crud
from database import get_db
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import and_
from typing import Optional, List

load_dotenv()

router = APIRouter()

GITHUB_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
if not GITHUB_SECRET:
    raise RuntimeError("GITHUB_WEBHOOK_SECRET is not set")

@router.post("/webhooks/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(...),
    x_hub_signature_256: str = Header(None),
    db: Session = Depends(get_db)
):
    body = await request.body()

    # Validate Signature
    if x_hub_signature_256:
        expected_signature = 'sha256=' + hmac.new(GITHUB_SECRET.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_signature, x_hub_signature_256):
            raise HTTPException(status_code=400, detail="Invalid signature")

    payload = await request.json()
    print(f"[webhook] Event: {x_github_event}")

    await dispatch_event(x_github_event, payload, db)

    return {"message": "Webhook received"}

@router.get("/webhooks/logs", response_model=List[GitHubEventLogOut])
def get_logs(
    event_type: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    delivery_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    return github_event_crud.get_filtered_events(
        db,
        event_type=event_type,
        from_date=from_date,
        to_date=to_date,
        delivery_id=delivery_id
    )