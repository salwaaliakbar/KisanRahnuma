"""WhatsApp Business Cloud API channel: Meta webhook payloads <-> the engine's internal types.

Does the same job as channels/web.py for the web simulator. No business logic lives here.

Inbound (webhook "messages" entries):
    text                         -> InboundMessage(kind=TEXT, text=body)
    interactive.button_reply.id  -> InboundMessage(kind=OPTION, option_id=id)
    interactive.list_reply.id    -> InboundMessage(kind=OPTION, option_id=id)
    button.payload (template)    -> InboundMessage(kind=OPTION, option_id=payload)
    audio / voice                -> InboundMessage(kind=VOICE)
    anything else (image, ...)   -> InboundMessage(kind=TEXT, text=None) -> "not understood"
    external_ref = sender's wa_id (hashed by ConsentService), message_id = wamid (dedupe)

Outbound (one OutboundMessage -> usually one WhatsApp message):
    no options                   -> text message
    feedback answer              -> reply buttons [Yes, helpful] [Not helpful] [Home]
    1..3 options                 -> reply buttons
    4..10 options                -> list message
    text over 1,024 characters with options -> a text message, then the buttons/list
                                   (the engine keeps texts shorter, so this is a safety net)
"""
from collections.abc import Iterator
from typing import Any

from app.domain.messages import (
    MAX_INTERACTIVE_TEXT,
    InboundKind,
    InboundMessage,
    Option,
    OutboundMessage,
    feedback_option_id,
)
from app.i18n import t

CHANNEL = "whatsapp"
MAX_BUTTONS = 3
MAX_BUTTON_TITLE = 20
MAX_ROW_TITLE = 24
MAX_TEXT = 4096  # plain text message body limit

Payload = dict[str, Any]


# ---------------------------------------------------------------------- inbound
def iter_messages(webhook: Payload, phone_number_id: str | None = None) -> Iterator[Payload]:
    """Every incoming farmer message in a webhook body.

    Delivery/read status updates ("statuses") are skipped. When `phone_number_id` is given,
    messages sent to other numbers on the same Meta app are skipped too.
    """
    if webhook.get("object") != "whatsapp_business_account":
        return
    for entry in webhook.get("entry") or []:
        for change in entry.get("changes") or []:
            if change.get("field") != "messages":
                continue
            value = change.get("value") or {}
            to_number = (value.get("metadata") or {}).get("phone_number_id")
            if phone_number_id and to_number and to_number != phone_number_id:
                continue
            yield from value.get("messages") or []


def to_inbound(message: Payload) -> InboundMessage:
    kind, text, option_id = InboundKind.TEXT, None, None
    match message.get("type"):
        case "text":
            text = (message.get("text") or {}).get("body")
        case "interactive":
            interactive = message.get("interactive") or {}
            reply = interactive.get("button_reply") or interactive.get("list_reply") or {}
            option_id = reply.get("id")
            kind = InboundKind.OPTION if option_id else InboundKind.TEXT
        case "button":  # quick-reply button on a template message
            button = message.get("button") or {}
            option_id = button.get("payload")
            text = None if option_id else button.get("text")
            kind = InboundKind.OPTION if option_id else InboundKind.TEXT
        case "audio" | "voice":
            kind = InboundKind.VOICE
    return InboundMessage(
        channel=CHANNEL,
        external_ref=message["from"],
        kind=kind,
        text=text,
        option_id=option_id,
        message_id=message.get("id"),
    )


# ---------------------------------------------------------------------- outbound
def to_whatsapp(message: OutboundMessage, lang: str) -> list[Payload]:
    """The Cloud API message bodies (without "to") for one engine reply."""
    options = _options_with_feedback(message, lang)
    text = message.text.strip()
    if not options:
        return [_text(text)]

    payloads: list[Payload] = []
    if len(text) > MAX_INTERACTIVE_TEXT:
        payloads.append(_text(text))
        text = t("list_button", lang)  # interactive messages need a body; keep it short
    if len(options) <= MAX_BUTTONS:
        payloads.append(_buttons(text, options))
    else:
        payloads.append(_list(text, options, lang))
    return payloads


def _options_with_feedback(message: OutboundMessage, lang: str) -> list[Option]:
    if not message.feedback:
        return list(message.options)
    service = message.service or "unknown"
    feedback = [
        Option(feedback_option_id(True, service, message.id), t("feedback_yes", lang)),
        Option(feedback_option_id(False, service, message.id), t("feedback_no", lang)),
    ]
    return [*feedback, *message.options]  # + Home: 3 buttons in the SAME message as the answer


def _fit(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def _text(body: str) -> Payload:
    return {"type": "text", "text": {"body": _fit(body, MAX_TEXT), "preview_url": False}}


def _buttons(body: str, options: list[Option]) -> Payload:
    return {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": o.id, "title": _fit(o.label, MAX_BUTTON_TITLE)}} for o in options
                ]
            },
        },
    }


def _list(body: str, options: list[Option], lang: str) -> Payload:
    return {
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": body},
            "action": {
                "button": _fit(t("list_button", lang), MAX_BUTTON_TITLE),
                "sections": [{"rows": [{"id": o.id, "title": _fit(o.label, MAX_ROW_TITLE)} for o in options]}],
            },
        },
    }
