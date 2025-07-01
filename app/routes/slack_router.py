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
from models.slack_mapping import SlackProjectMap
from app.schemas.slack_mapping import SlackMappingCreate 

router = APIRouter()

@router.post("/webhooks/slack")
async def slack_events(request: Request, db: Session = Depends(get_db)):
    raw_body = await request.body()
    verify_slack_signature(request, raw_body)

    payload = await request.json()

    if payload.get("type") == "url_verification":
        return JSONResponse(content={"challenge": payload["challenge"]})

    event = payload.get("event", {})

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
        notify_channel_about_event(payload)

    return {"status": "ok"}


@router.get("/messages", response_model=List[SlackMessageRead])
def list_messages(db: Session = Depends(get_db)):
    return db.query(SlackMessage).all()


@router.post("/admin/slack/mapping")
def create_slack_mapping(mapping: SlackMappingCreate, db: Session = Depends(get_db)):
    new_map = SlackProjectMap(
        project_id=mapping.project_id,
        slack_channel_id=mapping.slack_channel_id
    )
    db.add(new_map)
    db.commit()
    return {"status": "Mapping added successfully"}
 
