import os
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from src.app.middleware_sec import SecurityHeadersMiddleware
from src.app.routers import router
from src.exceptions.base import ApiException

app = FastAPI(title="Secure Team Voting Board", version="0.5.2")

# Trusted Host Middleware
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT == "production":
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "").split(",")
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# CORS Middleware
if ENVIRONMENT == "development":
    origins = [
        "http://localhost:*",
        "http://127.0.0.1:*",
        "http://localhost:8080",  # Адрес веб-апи
    ]
else:
    origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware, environment=ENVIRONMENT)


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
