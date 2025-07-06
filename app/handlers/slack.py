from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from app.crud import slack_crud
from app.schemas.slack import SlackMessageCreate
from app.services.slack_service import notify_channel_about_event

async def handle_slack_event(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()

    if payload.get("type") == "url_verification":
        return JSONResponse(content={"challenge": payload["challenge"]})

    event = payload.get("event", {})
    if event.get("subtype") == "bot_message" or event.get("bot_id"):
        return {"status": "ignored"}

    if event.get("type") == "message" and "subtype" not in event:
        slack_msg = SlackMessageCreate(
            id=payload.get("event_id"),
            user_id=event.get("user"),
            channel_id=event.get("channel"),
            text=event.get("text"),
            timestamp=event.get("ts")
        )
        slack_crud.create_slack_message(db, slack_msg)
        notify_channel_about_event(payload)

    return {"status": "ok"}
