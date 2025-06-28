from fastapi import FastAPI
from app.routes import user
from app.routes import project
from app.routes import task
from app.routes import auth_router
from app.routes import webhook_router
from app.routes import slack_router

app = FastAPI()

app.include_router(user.router)
app.include_router(project.router)
app.include_router(task.router)
app.include_router(auth_router.router)
app.include_router(webhook_router.router)
app.include_router(slack_router.router)


@app.get("/health-check")
def health_check():
    return {"status": "ok"}
