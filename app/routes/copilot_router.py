from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from database import get_db
from app.auth.dependencies import require_role
from models.user import User
from app.services.copilot_service import stream_copilot_response

router = APIRouter(prefix="/copilot", tags=["copilot"])


class CopilotMessage(BaseModel):
    role: str
    content: str


class CopilotRequest(BaseModel):
    messages: List[CopilotMessage]


@router.post("/chat")
async def copilot_chat(
    req: CopilotRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager", "developer")),
):
    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    return StreamingResponse(
        stream_copilot_response(messages, db, current_user.id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
