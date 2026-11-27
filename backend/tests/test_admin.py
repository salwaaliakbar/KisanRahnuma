import copy

from app.database.seed import seed
from app.services.data_loader import load_json


def test_login_wrong_password_rejected(client):
    assert client.post("/api/admin/login", json={"password": "nope"}).status_code == 401


def test_login_correct_password_issues_token(client):
    response = client.post("/api/admin/login", json={"password": "test-admin-password"})
    assert response.status_code == 200
    assert response.json()["token"]


def test_content_requires_admin_login(client):
    assert client.get("/api/admin/content/crop_rates.json").status_code == 401


def test_unknown_content_file_rejected(client, admin_headers):
    assert client.get("/api/admin/content/not_a_file.json", headers=admin_headers).status_code == 404


def test_content_roundtrip_and_cache_invalidation(client, admin_headers, isolated_content_dir):
    original = client.get("/api/admin/content/crop_rates.json", headers=admin_headers).json()["content"]
    updated = copy.deepcopy(original)
    updated["crops"][0]["rates"]["sukkur"]["rate"] = 12345

    put = client.put(
        "/api/admin/content/crop_rates.json", json={"content": updated}, headers=admin_headers
    )
    assert put.status_code == 200
    assert put.json()["content"]["crops"][0]["rates"]["sukkur"]["rate"] == 12345

    # load_json's cache was cleared, so a fresh read (as the conversation engine does) sees the edit.
    assert load_json("crop_rates.json")["crops"][0]["rates"]["sukkur"]["rate"] == 12345


def test_farmers_list_requires_admin_login(client):
    assert client.get("/api/admin/farmers").status_code == 401


def test_farmers_list(client, db, admin_headers):
    seed(db, farmers=5)
    response = client.get("/api/admin/farmers?limit=3", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 3
    assert all("farmer_id" in item for item in data["items"])
