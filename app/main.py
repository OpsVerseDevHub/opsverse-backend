from fastapi import FastAPI

app = FastAPI()
from fastapi import FastAPI
from app.routes import user  # adjust this to your actual path

app = FastAPI()

app.include_router(user.router)


@app.get("/health-check")
def health_check():
    return {"status": "ok"}