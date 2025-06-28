from fastapi import APIRouter, Request, Depends, HTTPException
from starlette.responses import JSONResponse
from app.handlers.slack import handle_slack_event
from models.slack import SlackMessage
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from app.schemas.slack import SlackMessageRead
from app.crud import slack_crud 
from app.schemas.slack import SlackMessageCreate
from app.services.slack_service import notify_channel_about_event
from app.utils.slack_verify import verify_slack_signature

router = APIRouter()

@router.post("/webhooks/slack")
async def slack_events(request: Request, db: Session = Depends(get_db)):
    raw_body = await request.body()
    verify_slack_signature(request, raw_body)  # 🔐 Verify Slack authenticity

    payload = await request.json()

    # Slack URL verification
    if payload.get("type") == "url_verification":
        return JSONResponse(content={"challenge": payload["challenge"]})

    event = payload.get("event", {})

    # ✅ Ignore messages from bots (loop prevention)
    if event.get("subtype") == "bot_message" or event.get("bot_id"):
        return {"status": "ignored"}

    if event.get("type") == "message" and "subtype" not in event:
        slack_msg = SlackMessageCreate(
            id=payload["event_id"],
            user_id=event["user"],
            channel_id=event["channel"],
            text=event["text"],
            timestamp=event["ts"]
        )
        slack_crud.create_slack_message(db=db, message_data=slack_msg)
        
        await notify_channel_about_event(payload)

    return {"status": "ok"}


@router.get("/messages", response_model=List[SlackMessageRead])
def list_messages(db: Session = Depends(get_db)):
    return db.query(SlackMessage).all()
