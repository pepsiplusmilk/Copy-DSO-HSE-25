import os
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from src.adapters.logger import logger, mask_pii
from src.app.routers import router
from src.exceptions.base import ApiException
from src.middleware.cors_policy import SecurityHeadersMiddleware
from src.middleware.ratelimits import (
    RequestTimeoutMiddleware,
    create_rate_limit_response,
    get_limiter,
)

app = FastAPI(title="Secure Team Voting Board", version="0.6.2")


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


# Rate Limiting Middleware
limiter = get_limiter()
app.state.limiter = limiter

app.add_middleware(RequestTimeoutMiddleware, timeout=30.0)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return create_rate_limit_response(request, exc)


## Errors handling


def format_to_RFC(status: int, title: str, detail: str, error_type: str = "about:blank"):
    corr_id = str(uuid.uuid4())

    logger.error(
        f"API raised an error with code: {status}",
        extra={
            "type": error_type,
            "correlation_id": corr_id,
            "status": status,
            "title": title,
            "detail": detail,
        },
    )

    return JSONResponse(
        status_code=status,
        content={
            "type": error_type,
            "title": title,
            "status": status,
            "detail": detail,
            "correlation_id": corr_id,
        },
        media_type="application/problem+json",
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    masked_errors = [mask_pii(err.copy()) for err in errors]

    return format_to_RFC(
        status=422,
        title="validation_error",
        detail=masked_errors,
        error_type="/errors/validation_error",
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
async def health(request: Request):
    return {"status": "ok"}
