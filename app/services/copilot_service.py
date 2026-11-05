import os
import json
import httpx
from typing import Generator
from sqlalchemy.orm import Session
from models.task import Task as TaskModel
from models.project import Project as ProjectModel

OLLAMA_BASE = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def _build_workspace_context(db: Session) -> str:
    projects = db.query(ProjectModel).limit(50).all()
    if not projects:
        return "No projects or tasks exist yet in this workspace."

    lines = ["=== LIVE WORKSPACE DATA ===\n"]

    for p in projects:
        tasks = db.query(TaskModel).filter(TaskModel.project_id == p.id).all()
        total = len(tasks)
        done = sum(1 for t in tasks if t.status == "done")
        blocked = sum(1 for t in tasks if t.status == "blocked")
        in_prog = sum(1 for t in tasks if t.status == "in_progress")
        todo = sum(1 for t in tasks if t.status == "todo")
        high = sum(1 for t in tasks if t.priority in ("high", "critical"))

        health = max(0, int((done / total * 100) - (blocked / total * 30))) if total else 0

        lines.append(f"PROJECT: {p.name} (id={p.id})")
        lines.append(f"  Tasks: {total} total | {done} done | {in_prog} in progress | {todo} todo | {blocked} blocked")
        lines.append(f"  High/Critical priority: {high}")
        lines.append(f"  Health score: {health}/100")

        blocked_tasks = [t for t in tasks if t.status == "blocked"]
        if blocked_tasks:
            lines.append(f"  Blocked tasks: " + ", ".join(f'"{t.title}"' for t in blocked_tasks[:5]))

        overdue = [t for t in tasks if t.due_date and t.status != "done"]
        if overdue:
            lines.append(f"  Open with due dates: " + ", ".join(
                f'"{t.title}" (due {t.due_date})' for t in overdue[:5]
            ))

        lines.append("")

    # Overall stats
    all_tasks = db.query(TaskModel).all()
    total_all = len(all_tasks)
    done_all = sum(1 for t in all_tasks if t.status == "done")
    blocked_all = sum(1 for t in all_tasks if t.status == "blocked")

    lines.append("=== WORKSPACE SUMMARY ===")
    lines.append(f"Projects: {len(projects)}")
    lines.append(f"Total tasks: {total_all} | Done: {done_all} | Blocked: {blocked_all}")
    if total_all:
        lines.append(f"Overall completion: {done_all / total_all:.0%}")

    return "\n".join(lines)


def _build_system_prompt(context: str) -> str:
    return f"""You are OpsVerse IQ, an embedded AI co-pilot for a project management platform.

You have been given a live snapshot of the workspace data below. Use it to answer questions accurately and directly. When you cite numbers, pull them from the data. Be concise and analytical.

{context}

Rules:
- Answer based on the data above. If something isn't in the data, say so.
- Use markdown sparingly — bullet lists are fine, avoid heavy headers.
- Keep responses tight. No fluff."""


def stream_copilot_response(
    messages: list,
    db: Session,
    current_user_id: int,
) -> Generator[str, None, None]:
    # Check Ollama is reachable
    try:
        with httpx.Client(timeout=3.0) as probe:
            probe.get(f"{OLLAMA_BASE}/api/tags")
    except Exception:
        yield f"data: {json.dumps({'type': 'error', 'text': f'Ollama is not running. Start it with: ollama serve (then: ollama pull {OLLAMA_MODEL})'})}\n\n"
        return

    # Build live context from DB
    try:
        context = _build_workspace_context(db)
    except Exception as e:
        context = f"(Could not load workspace data: {e})"

    system_prompt = _build_system_prompt(context)

    payload = {
        "model": OLLAMA_MODEL,
        "stream": True,
        "messages": [
            {"role": "system", "content": system_prompt},
            *messages,
        ],
        "options": {
            "temperature": 0.3,
            "num_predict": 1024,
        },
    }

    try:
        with httpx.Client(timeout=120.0) as client:
            with client.stream(
                "POST",
                f"{OLLAMA_BASE}/api/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
            ) as resp:
                if resp.status_code != 200:
                    err = resp.read().decode()
                    if "model" in err.lower() and ("not found" in err.lower() or "pull" in err.lower()):
                        yield f"data: {json.dumps({'type': 'error', 'text': f'Model \"{OLLAMA_MODEL}\" not found. Run: ollama pull {OLLAMA_MODEL}'})}\n\n"
                    else:
                        yield f"data: {json.dumps({'type': 'error', 'text': f'Ollama error {resp.status_code}: {err[:200]}'})}\n\n"
                    return

                for line in resp.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    token = chunk.get("message", {}).get("content", "")
                    if token:
                        yield f"data: {json.dumps({'type': 'text', 'text': token})}\n\n"

                    if chunk.get("done"):
                        break

    except httpx.ReadTimeout:
        yield f"data: {json.dumps({'type': 'error', 'text': 'Ollama timed out. The model may still be loading — try again in a moment.'})}\n\n"
        return
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'text': f'Connection error: {str(e)}'})}\n\n"
        return

    yield f"data: {json.dumps({'type': 'done'})}\n\n"
