import uuid

from app.database.seed import seed


def chat(client, client_id, **body):
    response = client.post("/api/chat", json={"client_id": client_id, **body})
    assert response.status_code == 200, response.text
    return response.json()


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}
    assert client.get("/health").json() == {"status": "ok"}
    assert client.head("/health").status_code == 200


def test_chat_validation_errors(client):
    assert client.post("/api/chat", json={"client_id": "not-a-uuid", "text": "hi"}).status_code == 422
    assert client.post("/api/chat", json={"client_id": str(uuid.uuid4())}).status_code == 422


def test_chat_feedback_and_consent_endpoints(client):
    cid = str(uuid.uuid4())
    data = chat(client, cid, text="hi")
    assert data["state"] == "CHOOSE_LANGUAGE"
    data = chat(client, cid, option_id="lang:en")
    assert data["state"] == "CHOOSE_DISTRICT" and data["language"] == "en"
    data = chat(client, cid, option_id="district:sukkur")
    assert data["state"] == "CONSENT"
    data = chat(client, cid, option_id="consent:both")
    assert data["state"] == "MAIN_MENU"

    chat(client, cid, option_id="menu:weather")
    answer = chat(client, cid, option_id="district:sukkur")["messages"][0]
    assert answer["feedback"] is True

    fb = client.post(
        "/api/feedback",
        json={"client_id": cid, "response_id": answer["id"], "service": answer["service"], "helpful": False},
    )
    assert fb.status_code == 200 and fb.json()["linked_to_farmer"] is True

    consent = client.get(f"/api/consent/{cid}").json()
    assert consent["usage_consent"] is True and consent["weekly_updates"] is True

    updated = client.post("/api/consent", json={"client_id": cid, "weekly_updates": False}).json()
    assert updated["weekly_updates"] is False


def test_unknown_farmer_returns_404(client):
    assert client.get(f"/api/consent/{uuid.uuid4()}").status_code == 404


def test_dashboard_summary_requires_admin_login(client):
    assert client.get("/api/dashboard/summary").status_code == 401


def test_dashboard_summary(client, db, admin_headers):
    seed(db, farmers=10)
    data = client.get("/api/dashboard/summary", headers=admin_headers).json()
    assert data["total_farmers"] == 10
    assert len(data["service_usage"]) == 5
    assert data["feedback"]["helpful"] + data["feedback"]["not_helpful"] > 0
    assert all(len(r["farmer_ref"]) == 8 for r in data["recent_interactions"])


def test_message_usage_endpoint(client, admin_headers):
    chat(client, str(uuid.uuid4()), text="hi")
    data = client.get("/api/dashboard/messages", headers=admin_headers).json()
    assert data["sent_by_channel"] == {"web": 1}
    assert data["whatsapp_sent"] == 0
    assert data["whatsapp_free_remaining"] == data["whatsapp_free_limit"] == 1000
