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
│
├── app/
│   └── main.py
│
├── venv/                  # Local Python environment (ignored)
├── .env                   # Environment variables (ignored)
├── .gitignore
├── README.md
```
