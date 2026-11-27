"""WhatsApp Business Cloud API webhook.

    GET  /api/whatsapp/webhook   Meta's one-time verification (hub.challenge)
    POST /api/whatsapp/webhook   incoming messages -> ConversationService -> replies via the Graph API

The farmer's message is handled during the request (it only touches the database, so it
is fast and the redelivery check is committed before we answer). The replies are sent to
Meta in a background task after the 200 response, because Meta expects a quick answer and
retries webhooks that are slow or fail.
"""
import hashlib
import hmac
import json
import logging
from typing import Any

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.channels import whatsapp
from app.core.config import Settings, get_settings
from app.database.session import get_db
from app.services.conversation_service import ConversationService

logger = logging.getLogger("farmer_assistant.whatsapp")
router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])


class WhatsAppClient:
    """Sends messages through the Cloud API (/{phone_number_id}/messages)."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.url = f"https://graph.facebook.com/{settings.whatsapp_api_version}/{settings.whatsapp_phone_number_id}/messages"

    def send(self, to: str, payloads: list[dict[str, Any]]) -> None:
        headers = {"Authorization": f"Bearer {self.settings.whatsapp_access_token}"}
        with httpx.Client(timeout=15) as client:
            for payload in payloads:  # in order: a long text first, then its buttons
                body = {"messaging_product": "whatsapp", "recipient_type": "individual", "to": to, **payload}
                try:
                    response = client.post(self.url, headers=headers, json=body)
                except httpx.HTTPError:
                    logger.exception("Could not reach the WhatsApp Cloud API")
                    return
                if response.is_error:
                    _log_api_error(response)
                    return  # don't send the buttons if the text before them failed


def _log_api_error(response: httpx.Response) -> None:
    try:
        error = response.json().get("error", {})
    except ValueError:
        error = {}
    hint = ""
    if error.get("code") == 190:
        hint = " -> the access token is invalid or expired (test tokens last 24 hours); update ACCESS_TOKEN in .env"
    elif error.get("code") == 131030:
        hint = " -> this number is not in the test recipient list (WhatsApp -> API Setup -> 'To')"
    logger.error("WhatsApp send failed (%s): %s%s", response.status_code, error.get("message", response.text), hint)


def get_whatsapp_client(settings: Settings = Depends(get_settings)) -> WhatsAppClient:
    return WhatsAppClient(settings)


def signature_is_valid(body: bytes, header: str | None, app_secret: str) -> bool:
    if not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.removeprefix("sha256="))


@router.get("/webhook", response_class=PlainTextResponse)
def verify(
    mode: str = Query("", alias="hub.mode"),
    token: str = Query("", alias="hub.verify_token"),
    challenge: str = Query("", alias="hub.challenge"),
    settings: Settings = Depends(get_settings),
) -> str:
    """Meta calls this once when you click "Verify and save" in the webhook settings."""
    if not settings.whatsapp_verify_token:
        logger.error("WhatsApp verification refused: set VERIFY_TOKEN in backend/.env")
        raise HTTPException(status_code=403, detail="Verify token not configured")
    if mode != "subscribe" or not hmac.compare_digest(token, settings.whatsapp_verify_token):
        raise HTTPException(status_code=403, detail="Verification failed")
    return challenge


@router.post("/webhook")
async def receive(
    request: Request,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    client: WhatsAppClient = Depends(get_whatsapp_client),
) -> dict[str, str]:
    body = await request.body()
    if not settings.whatsapp_app_secret:
        # Without the secret anyone who finds the URL could make the bot send (billed) messages.
        logger.error("WhatsApp webhook refused: set APP_SECRET in backend/.env (Meta App settings -> Basic)")
        raise HTTPException(status_code=503, detail="App secret not configured")
    if not signature_is_valid(body, request.headers.get("X-Hub-Signature-256"), settings.whatsapp_app_secret):
        raise HTTPException(status_code=401, detail="Invalid signature")
    try:
        webhook = json.loads(body)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON") from None

    # The engine uses blocking database calls, so it runs in a worker thread.
    for to, payloads in await run_in_threadpool(handle_webhook, webhook, db, settings):
        background.add_task(client.send, to, payloads)
    return {"status": "ok"}


def handle_webhook(webhook: dict[str, Any], db: Session, settings: Settings) -> list[tuple[str, list[dict[str, Any]]]]:
    """Run every farmer message through the engine; returns (recipient, Cloud API payloads) to send."""
    outgoing = []
    for raw in whatsapp.iter_messages(webhook, settings.whatsapp_phone_number_id or None):
        try:
            inbound = whatsapp.to_inbound(raw)
            result = ConversationService(db, settings).handle(inbound)
        except SQLAlchemyError:
            raise  # 503: Meta retries later, and the redelivery check makes that safe
        except Exception:  # noqa: BLE001 - one bad message must not block the others
            db.rollback()
            logger.exception("Could not handle WhatsApp message %s", raw.get("id"))
            continue
        payloads = [p for m in result.messages for p in whatsapp.to_whatsapp(m, result.language)]
        if payloads:
            outgoing.append((inbound.external_ref, payloads))
    return outgoing
