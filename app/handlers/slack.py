from fastapi import Request
from fastapi.responses import JSONResponse
from app.crud import slack_crud
from database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from app.schemas.slack import SlackMessageCreate

async def handle_slack_event(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    
    if payload.get("type") == "url_verification":
        return JSONResponse(content={"challenge": payload["challenge"]})
    
    event = payload.get("event", {})
    if event.get("type") == "message" and "subtype" not in event:
        slack_msg = SlackMessageCreate(
            user_id=event.get("user"),
            channel_id=event.get("channel"),
            text=event.get("text"),
            timestamp=event.get("ts")
            )
        slack_crud.create_slack_message(db, message_data=slack_msg)

    return {"status": "ok"}
