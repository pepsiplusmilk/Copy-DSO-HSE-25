import asyncio
import uuid

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


def get_limiter():
    return Limiter(
        key_func=get_remote_address,
        default_limits=["100/minute"],
    )


def create_rate_limit_response(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    retry_after = 60

    return JSONResponse(
        status_code=429,
        content={
            "type": "/errors/too_many_requests",
            "title": "Too Many Requests",
            "status": 429,
            "detail": f"Rate limit exceeded. Please retry after {retry_after} seconds.",
            "correlation_id": str(uuid.uuid4()),
        },
        headers={"Retry-After": str(retry_after)},
    )


class RequestTimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout: float = 30.0):
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next):
        try:
            response = await asyncio.wait_for(call_next(request), timeout=self.timeout)
            return response

        except asyncio.TimeoutError:

            return JSONResponse(
                status_code=504,
                content={
                    "type": "errors/timeout",
                    "title": "Gateway Timeout",
                    "status": 504,
                    "detail": f"Request processing exceeded {self.timeout} seconds timeout.",
                    "correlation_id": str(uuid.uuid4()),
                },
            )
