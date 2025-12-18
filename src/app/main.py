import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from src.app.routers import router
from src.exceptions.base import ApiException

app = FastAPI(title="Secure Team Voting Board", version="0.5.0")


def format_to_RFC(status: int, title: str, detail: str, error_type: str = "about:blank"):
    return JSONResponse(
        status_code=status,
        content={
            "type": error_type,
            "title": title,
            "status": status,
            "detail": detail,
            "correlation_id": str(uuid.uuid4()),
        },
        media_type="application/problem+json",
    )


@app.exception_handler(ApiException)
async def api_error_handler(request: Request, exc: ApiException):
    return format_to_RFC(
        status=exc.status_code,
        title=exc.code,
        detail=exc.message,
        error_type=f"/errors/{exc.code}",
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Normalize FastAPI HTTPException into our error envelope
    detail = exc.detail if isinstance(exc.detail, str) else "Unexpected error"
    return format_to_RFC(
        status=exc.status_code,
        title="http_error",
        detail=detail,
    )


app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
