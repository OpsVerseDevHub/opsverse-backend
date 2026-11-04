import re
from sqlalchemy.orm import Session
from app.crud import task as task_crud
from app.crud.task import update_task_with_commit
from typing import Optional


def extract_task_id_from_message(message: str) -> Optional[int]:
    match = re.search(r"(?:#|TASK-)(\d+)", message)
    return int(match.group(1)) if match else None


async def handle_push(payload: dict, db: Session):
    ref = payload.get("ref", "")
    pusher = payload.get("pusher", {}).get("name")
    repo = payload.get("repository", {}).get("full_name")
    commits = payload.get("commits", [])

    print(f"[push] {pusher} pushed to {ref} in {repo}")

    for commit in commits:
        message = commit.get("message", "")
        commit_hash = commit.get("id", "")
        updated_task = update_task_with_commit(db, message, commit_hash)
        if updated_task:
            print(f"[push] Task #{updated_task.id} linked to commit {commit_hash[:7]}")


async def handle_pull_request(payload: dict, db: Session):
    action = payload.get("action")
    pr_number = payload.get("number")
    pr_title = payload.get("pull_request", {}).get("title", "")
    user = payload.get("sender", {}).get("login")
    print(f"[pr] #{pr_number} '{pr_title}' {action} by {user}")

    task_id = extract_task_id_from_message(pr_title)
    if task_id and action in ("opened", "closed"):
        new_status = "review" if action == "opened" else "done"
        task_crud.update_task_status(db, task_id, new_status)
        print(f"[pr] Task #{task_id} → {new_status}")


async def handle_issues(payload: dict, db: Session):
    action = payload.get("action")
    issue = payload.get("issue", {})
    title = issue.get("title", "")
    number = issue.get("number")
    user = payload.get("sender", {}).get("login")
    print(f"[issue] #{number} '{title}' {action} by {user}")

    task_id = extract_task_id_from_message(title)
    if task_id and action == "closed":
        task_crud.update_task_status(db, task_id, "done")
        print(f"[issue] Task #{task_id} → done")
