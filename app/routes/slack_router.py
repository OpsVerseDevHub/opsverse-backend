from fastapi import APIRouter, Request, Depends
from starlette.responses import JSONResponse
from app.handlers.slack import handle_slack_event
from models.slack import SlackMessage
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from app.schemas.slack import SlackMessageRead
from app.crud import slack_crud 
from app.schemas.slack import SlackMappingCreate
from models.slack_mapping import SlackProjectMap
from app.utils.slack_verify import verify_slack_signature

router = APIRouter()

@router.post("/webhooks/slack")
async def slack_events(request: Request, db: Session = Depends(get_db)):
    raw_body = await request.body()
    verify_slack_signature(request, raw_body)
    return await handle_slack_event(request, db)


@router.get("/messages", response_model=List[SlackMessageRead])
def list_messages(
    db: Session = Depends(get_db),
    project_id: int = None,
    channel_id: str = None,
    limit: int = 50,
    offset: int = 0
):
    query = db.query(SlackMessage)
    if project_id:
        query = query.filter(SlackMessage.project_id == project_id)
    if channel_id:
        query = query.filter(SlackMessage.channel_id == channel_id)
    return query.offset(offset).limit(limit).all()


@router.post("/admin/slack/mapping")
def create_slack_mapping(mapping: SlackMappingCreate, db: Session = Depends(get_db)):
    new_map = SlackProjectMap(
        project_id=mapping.project_id,
        slack_channel_id=mapping.slack_channel_id
    )
    db.add(new_map)
    db.commit()
    return {"status": "Mapping added successfully"}


@router.get("/admin/slack/mapping")
def list_slack_mappings(db: Session = Depends(get_db)):
    return db.query(SlackProjectMap).all()
