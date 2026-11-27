"""WhatsApp webhook and adapter, with sample Meta payloads and a fake sender (nothing reaches Meta)."""
import hashlib
import hmac
import json

import pytest
from sqlalchemy import func, select

from app.api.whatsapp_webhook import get_whatsapp_client
from app.channels import whatsapp
from app.core.config import get_settings
from app.domain.messages import Option, OutboundMessage
from app.i18n import SUPPORTED_LANGUAGES, t
from app.main import app
from app.models import Feedback

SECRET, VERIFY, PHONE_ID, FARMER = "app-secret", "verify-me", "1234567890", "923001234567"


class FakeClient:
    def __init__(self):
        self.sent = []  # (to, payload)

    def send(self, to, payloads):
        self.sent.extend((to, p) for p in payloads)


@pytest.fixture
def wa(client):
    settings = get_settings().model_copy(
        update={"whatsapp_app_secret": SECRET, "whatsapp_verify_token": VERIFY, "whatsapp_phone_number_id": PHONE_ID}
    )
    fake = FakeClient()
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_whatsapp_client] = lambda: fake
    return client, fake


def webhook(*messages, phone_id=PHONE_ID, statuses=None):
    value = {"messaging_product": "whatsapp", "metadata": {"phone_number_id": phone_id}}
    if messages:
        value["contacts"] = [{"wa_id": FARMER, "profile": {"name": "Test"}}]
        value["messages"] = list(messages)
    if statuses:
        value["statuses"] = statuses
    return {"object": "whatsapp_business_account", "entry": [{"id": "waba", "changes": [{"field": "messages", "value": value}]}]}


_counter = iter(range(10_000))


def text(body):
    return {"from": FARMER, "id": f"wamid.{next(_counter)}", "type": "text", "text": {"body": body}}


def tap(option_id, kind="button_reply"):
    return {"from": FARMER, "id": f"wamid.{next(_counter)}", "type": "interactive",
            "interactive": {"type": kind, kind: {"id": option_id, "title": "x"}}}


def post(client, payload, secret=SECRET):
    body = json.dumps(payload).encode()
    signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return client.post("/api/whatsapp/webhook", content=body,
                       headers={"Content-Type": "application/json", "X-Hub-Signature-256": signature})


def send(wa, message):
    client, fake = wa
    fake.sent.clear()
    assert post(client, webhook(message)).status_code == 200
    return [p for _, p in fake.sent]


def option_ids(payload):
    action = payload["interactive"]["action"]
    if "buttons" in action:
        return [b["reply"]["id"] for b in action["buttons"]]
    return [r["id"] for r in action["sections"][0]["rows"]]


def onboard(wa):
    send(wa, text("Hi"))
    send(wa, tap("lang:en"))
    send(wa, tap("district:sukkur", "list_reply"))
    return send(wa, tap("consent:both"))


# ---------------------------------------------------------------------- verification & security
def test_meta_verification(wa):
    client, _ = wa
    params = {"hub.mode": "subscribe", "hub.verify_token": VERIFY, "hub.challenge": "12345"}
    r = client.get("/api/whatsapp/webhook", params=params)
    assert r.status_code == 200 and r.text == "12345"
    assert client.get("/api/whatsapp/webhook", params={**params, "hub.verify_token": "wrong"}).status_code == 403


def test_unsigned_or_forged_webhooks_are_rejected(wa):
    client, fake = wa
    assert post(client, webhook(text("Hi")), secret="forged").status_code == 401
    r = client.post("/api/whatsapp/webhook", json=webhook(text("Hi")))
    assert r.status_code == 401
    assert fake.sent == []


def test_webhook_refused_without_app_secret(client):
    app.dependency_overrides[get_settings] = lambda: get_settings().model_copy(update={"whatsapp_app_secret": ""})
    assert post(client, webhook(text("Hi"))).status_code == 503


# ---------------------------------------------------------------------- conversation over WhatsApp
def test_full_flow_uses_buttons_and_lists(wa):
    [picker] = send(wa, text("Hi"))
    assert picker["type"] == "interactive" and picker["interactive"]["type"] == "button"
    assert option_ids(picker) == ["lang:en", "lang:ur", "lang:sd"]

    [menu] = onboard(wa)
    assert menu["interactive"]["type"] == "list"  # 7 options -> list message
    assert menu["interactive"]["action"]["button"] == "Choose"
    assert "menu:weather" in option_ids(menu)

    [answer] = send(wa, tap("menu:weather", "list_reply"))  # saved district: answers straight away
    ids = option_ids(answer)
    assert answer["interactive"]["type"] == "button" and len(ids) == 3
    assert ids[0].startswith("fb:y:weather:") and ids[1].startswith("fb:n:weather:") and ids[2] == "nav:home"

    [after_vote] = send(wa, tap(ids[0]))
    assert "Thank you" in after_vote["interactive"]["body"]["text"]


def test_feedback_tap_is_saved(wa, db):
    onboard(wa)
    [answer] = send(wa, tap("menu:weather", "list_reply"))
    send(wa, tap(option_ids(answer)[0]))
    assert db.scalar(select(func.count()).select_from(Feedback)) == 1


def test_redelivered_webhook_gets_no_second_reply(wa):
    client, fake = wa
    message = text("Hi")
    post(client, webhook(message))
    fake.sent.clear()
    post(client, webhook(message))  # Meta retry: same wamid
    assert fake.sent == []


def test_status_updates_and_other_numbers_are_ignored(wa):
    client, fake = wa
    post(client, webhook(statuses=[{"id": "wamid.1", "status": "delivered", "recipient_id": FARMER}]))
    post(client, webhook(text("Hi"), phone_id="someone-else"))
    assert fake.sent == []


def test_voice_note_gets_a_reply(wa):
    onboard(wa)
    [reply] = send(wa, {"from": FARMER, "id": "wamid.voice", "type": "audio", "audio": {"id": "media-1"}})
    assert "nav:home" in option_ids(reply)


def test_replies_go_to_the_sender(wa):
    client, fake = wa
    post(client, webhook(text("Hi")))
    assert {to for to, _ in fake.sent} == {FARMER}


# ---------------------------------------------------------------------- adapter details
def test_long_text_is_sent_before_the_buttons():
    msg = OutboundMessage("x" * 1500, options=[Option("nav:home", "Home")])
    first, second = whatsapp.to_whatsapp(msg, "en")
    assert first["type"] == "text" and len(first["text"]["body"]) == 1500
    assert option_ids(second) == ["nav:home"]


def test_plain_text_without_options():
    [payload] = whatsapp.to_whatsapp(OutboundMessage("Hello"), "en")
    assert payload == {"type": "text", "text": {"body": "Hello", "preview_url": False}}


@pytest.mark.parametrize("lang", SUPPORTED_LANGUAGES)
def test_button_wording_fits_whatsapp_limits(lang):
    for key in ("feedback_yes", "feedback_no", "home", "list_button"):
        assert len(t(key, lang)) <= whatsapp.MAX_BUTTON_TITLE, (lang, key)
