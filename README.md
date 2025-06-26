# 🛠️ OpsVerse Backend

FastAPI-based backend service for OpsVerse MVP.

## 🔧 Tech Stack

- Python 3.9
- FastAPI
- PostgreSQL
- SQLAlchemy
- Uvicorn
- Alembic

## 🚀 Getting Started
Clone the repository
```bash
git clone https://github.com/OpsVerseDevHub/opsverse-backend.git
cd opsverse-backend
```
Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Mac/Linux
```
Install dependencies
```bash
pip install -r requirements.txt
```
🔍 Health Check
Run server locally:
```bash
uvicorn app.main:app --reload
```
Visit: http://127.0.0.1:8000/health-check

📁 Project Structure
```bash
opsverse-backend/
├── app/
│   ├── main.py                  # FastAPI app instance
│   ├── auth/                    # Auth logic (login, dependencies, utils)
│   ├── crud/                    # DB operations (User, Project, Task, GitHub Events)
│   ├── models/                  # SQLAlchemy models
│   ├── routes/                  # FastAPI route declarations
│   ├── schemas/                 # Pydantic models
│   ├── webhooks/               # GitHub event dispatcher and handlers
│   └── dependencies.py          # Reusable dependencies (e.g. DB session)
├── alembic/                     # DB migration versions
├── venv/                        # Virtual environment
├── .env                         # Secrets & DB URL
├── alembic.ini                  # Alembic config
├── database.py                  # DB engine and session setup
└── README.md                    # Project documentation
```

## 🔗 GitHub Webhook Integration

Set up a GitHub webhook listener to handle push events and update tasks automatically:
- Created a POST route at /webhooks/github
- Verified HMAC signatures using a shared secret
- Extracted task IDs from commit messages (TASK-5, #12)
- Synced task status in DB and recorded commit hash
💡 Used ngrok to expose localhost for GitHub webhook delivery:
```
ngrok http http://localhost:8000
```

## 🧪 Testing Webhooks with Postman

- Start your FastAPI server with Uvicorn:
```
uvicorn app.main:app --reload
```
- Use ngrok public URL in GitHub webhook (e.g. https://abc123.ngrok-free.app/webhooks/github)
- In Postman:
   Set method to POST
   URL: your-ngrok-url/webhooks/github
   Headers:

      Content-Type: application/json

      X-GitHub-Event: push

      X-GitHub-Delivery: test-id-001

   Body (raw JSON):
```
{
  "ref": "refs/heads/main",
  "repository": { "full_name": "OpsVerseDevHub/opsverse-backend" },
  "pusher": { "name": "OpsVerse-Dev" },
  "head_commit": {
    "id": "abc1234567890def",
    "message": "Fix bug in logic flow related to TASK-5"
  }
}
```
✅ If task ID is found, status updated in DB to in_progress and commit hash recorded. Idempotent logic avoids duplicate updates.

## 🧩 Database Schema Updates

- Added github_issue_id and commit_hash to Task model
- Auto-migrations via Alembic
- Logged events to github_events table for audit/debugging

## 📌 Notes

- Everything kept modular and simple (no config.py)
- .env used for secrets and DB URLs

