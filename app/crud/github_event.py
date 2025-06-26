from sqlalchemy.orm import Session
# from sqlalchemy import and_
from models.github_event import GitHubEvent
from typing import Optional, List
from datetime import datetime


def get_filtered_events(
    db: Session,
    event_type: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    delivery_id: Optional[str] = None,
    limit: int = 100,
) -> List[GitHubEvent]:
    query = db.query(GitHubEvent)

    if event_type:
        query = query.filter(GitHubEvent.event_type == event_type)

    if delivery_id:
        query = query.filter(GitHubEvent.delivery_id == delivery_id)

    if from_date:
        query = query.filter(GitHubEvent.received_at >= from_date)

    if to_date:
        query = query.filter(GitHubEvent.received_at <= to_date)

    return query.order_by(GitHubEvent.received_at.desc()).limit(limit).all()
