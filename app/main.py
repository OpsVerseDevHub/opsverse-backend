from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.routes import user, project, task, auth_router, webhook_router, slack_router

app = FastAPI(title="OpsVerse API", version="2.0.0")

app.include_router(user.router)
app.include_router(project.router)
app.include_router(task.router)
app.include_router(auth_router.router)
app.include_router(webhook_router.router)
app.include_router(slack_router.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(exc.body)},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/health-check")
def health_check():
    return {"status": "ok"}
