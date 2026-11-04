from .handlers import handle_push, handle_pull_request, handle_issues
from sqlalchemy.orm import Session


async def dispatch_event(event: str, payload: dict, db: Session):
    if event == "push":
        await handle_push(payload, db)
    elif event == "pull_request":
        await handle_pull_request(payload, db)
    elif event == "issues":
        await handle_issues(payload, db)
    else:
        print(f"[webhook] Unhandled event type: {event}")
