"""FastAPI application entry point.

Run from backend/:  uvicorn app.main:app --reload
"""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api import admin, chat, consent, dashboard, feedback, whatsapp_webhook
from app.core.config import get_settings

logger = logging.getLogger("farmer_assistant")
settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_origin_regex=settings.cors_origin_regex,
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(chat.router)
app.include_router(consent.router)
app.include_router(feedback.router)
app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(whatsapp_webhook.router)


@app.exception_handler(SQLAlchemyError)
async def database_error(_: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception("Database error", exc_info=exc)
    return JSONResponse(status_code=503, content={"detail": "Database is unavailable. Please try again."})


@app.api_route("/health", methods=["GET", "HEAD"], tags=["health"])
@app.api_route("/api/health", methods=["GET", "HEAD"], tags=["health"])
def health() -> dict[str, str]:
    """Liveness check for uptime monitors. HEAD is allowed because many monitors use it."""
    return {"status": "ok"}
