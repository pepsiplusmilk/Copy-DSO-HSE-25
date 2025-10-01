from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from src.app.routers import router
from src.domain.exceptions import ApiException

app = FastAPI(title="SecDev Course App", version="0.1.0")


@app.exception_handler(ApiException)
async def api_error_handler(request: Request, exc: ApiException):
    return JSONResponse(
        status_code=exc.status,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Normalize FastAPI HTTPException into our error envelope
    detail = exc.detail if isinstance(exc.detail, str) else "http_error"
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "http_error", "message": detail}},
    )


app.include_router(router)
