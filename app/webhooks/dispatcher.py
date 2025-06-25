from .handlers import handle_push, handle_pull_request
from sqlalchemy.orm import Session

async def dispatch_event(event: str, payload: dict, db: Session):
    if event == "push":
        await handle_push(payload, db)
    elif event == "pull_request":
        await handle_pull_request(payload, db)
    else:
        print(f"[webhook] Unhandled event type: {event}")
