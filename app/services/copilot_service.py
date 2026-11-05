import os
import json
from typing import Generator, Any
from sqlalchemy.orm import Session
from models.task import Task as TaskModel
from models.project import Project as ProjectModel
from models.user import User as UserModel

import anthropic

SYSTEM_PROMPT = """You are OpsVerse IQ, an AI co-pilot embedded in a project management platform.

You have access to tools that let you query the live database: projects, tasks, team metrics, and project health scores. Use them to give precise, data-backed answers.

Your personality: direct, analytical, slightly futuristic. No unnecessary filler. When you have numbers, show them.

Current platform: OpsVerse IQ — dev operations command center."""

TOOLS = [
    {
        "name": "get_projects",
        "description": "List all projects in the workspace with their status and task counts.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_tasks",
        "description": "Get tasks, optionally filtered by project or status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_id": {"type": "integer", "description": "Filter by project ID (optional)"},
                "status": {"type": "string", "description": "Filter by status: todo, in_progress, done, blocked (optional)"},
                "limit": {"type": "integer", "description": "Max tasks to return, default 20"}
            },
            "required": []
        }
    },
    {
        "name": "get_project_health",
        "description": "Get a health score and breakdown for a specific project.",
        "input_schema": {
            "type": "object",
            "properties": {
                "project_id": {"type": "integer", "description": "The project ID to analyse"}
            },
            "required": ["project_id"]
        }
    },
    {
        "name": "get_team_metrics",
        "description": "Get team-level metrics: total tasks, completion rate, tasks by priority, overdue count.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


def _run_tool(name: str, args: dict, db: Session, current_user_id: int) -> Any:
    if name == "get_projects":
        rows = db.query(ProjectModel).limit(50).all()
        result = []
        for p in rows:
            task_count = db.query(TaskModel).filter(TaskModel.project_id == p.id).count()
            done_count = db.query(TaskModel).filter(
                TaskModel.project_id == p.id, TaskModel.status == "done"
            ).count()
            result.append({
                "id": p.id,
                "name": p.name,
                "description": p.description or "",
                "total_tasks": task_count,
                "done_tasks": done_count,
            })
        return result

    if name == "get_tasks":
        q = db.query(TaskModel)
        if args.get("project_id"):
            q = q.filter(TaskModel.project_id == args["project_id"])
        if args.get("status"):
            q = q.filter(TaskModel.status == args["status"])
        limit = int(args.get("limit", 20))
        tasks = q.order_by(TaskModel.id.desc()).limit(limit).all()
        return [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
                "project_id": t.project_id,
                "assignee_id": t.assignee_id,
                "due_date": str(t.due_date) if t.due_date else None,
            }
            for t in tasks
        ]

    if name == "get_project_health":
        pid = args["project_id"]
        total = db.query(TaskModel).filter(TaskModel.project_id == pid).count()
        if total == 0:
            return {"project_id": pid, "health_score": 0, "detail": "No tasks found"}
        done = db.query(TaskModel).filter(TaskModel.project_id == pid, TaskModel.status == "done").count()
        blocked = db.query(TaskModel).filter(TaskModel.project_id == pid, TaskModel.status == "blocked").count()
        in_progress = db.query(TaskModel).filter(TaskModel.project_id == pid, TaskModel.status == "in_progress").count()
        completion_rate = done / total
        blocked_rate = blocked / total
        health = max(0, int((completion_rate * 100) - (blocked_rate * 30)))
        return {
            "project_id": pid,
            "health_score": health,
            "total": total,
            "done": done,
            "in_progress": in_progress,
            "blocked": blocked,
            "completion_rate": f"{completion_rate:.0%}",
        }

    if name == "get_team_metrics":
        total = db.query(TaskModel).count()
        done = db.query(TaskModel).filter(TaskModel.status == "done").count()
        blocked = db.query(TaskModel).filter(TaskModel.status == "blocked").count()
        high = db.query(TaskModel).filter(TaskModel.priority == "high").count()
        critical = db.query(TaskModel).filter(TaskModel.priority == "critical").count()
        return {
            "total_tasks": total,
            "done": done,
            "blocked": blocked,
            "completion_rate": f"{(done/total*100):.1f}%" if total else "0%",
            "high_priority": high,
            "critical_priority": critical,
        }

    return {"error": f"Unknown tool: {name}"}


def stream_copilot_response(
    messages: list,
    db: Session,
    current_user_id: int,
) -> Generator[str, None, None]:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        yield f"data: {json.dumps({'type': 'error', 'text': 'ANTHROPIC_API_KEY is not set. Add it to .env and restart the server.'})}\n\n"
        return

    client = anthropic.Anthropic(api_key=api_key)
    history = list(messages)

    while True:
        with client.messages.stream(
            model="claude-opus-5-5",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=history,
            thinking={"type": "adaptive"},
            output_config={"effort": "high"},
        ) as stream:
            tool_uses = []
            current_tool_use = None
            current_tool_input_json = ""

            for event in stream:
                # Stream text deltas to the client
                if event.type == "content_block_delta":
                    if event.delta.type == "text_delta":
                        yield f"data: {json.dumps({'type': 'text', 'text': event.delta.text})}\n\n"
                    elif event.delta.type == "input_json_delta":
                        current_tool_input_json += event.delta.partial_json

                elif event.type == "content_block_start":
                    if event.content_block.type == "tool_use":
                        current_tool_use = {
                            "id": event.content_block.id,
                            "name": event.content_block.name,
                        }
                        current_tool_input_json = ""
                        yield f"data: {json.dumps({'type': 'tool_start', 'tool': current_tool_use['name']})}\n\n"

                elif event.type == "content_block_stop":
                    if current_tool_use is not None:
                        try:
                            parsed_input = json.loads(current_tool_input_json) if current_tool_input_json else {}
                        except json.JSONDecodeError:
                            parsed_input = {}
                        current_tool_use["input"] = parsed_input
                        tool_uses.append(current_tool_use)
                        current_tool_use = None
                        current_tool_input_json = ""

            final_msg = stream.get_final_message()

        if final_msg.stop_reason != "tool_use":
            break

        # Execute all tools and loop
        history.append({"role": "assistant", "content": final_msg.content})

        tool_results = []
        for tu in tool_uses:
            result = _run_tool(tu["name"], tu.get("input", {}), db, current_user_id)
            yield f"data: {json.dumps({'type': 'tool_result', 'tool': tu['name']})}\n\n"
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu["id"],
                "content": json.dumps(result),
            })

        history.append({"role": "user", "content": tool_results})

    yield f"data: {json.dumps({'type': 'done'})}\n\n"
