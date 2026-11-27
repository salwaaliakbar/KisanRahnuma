"""Tests run against an in-memory SQLite database, so no PostgreSQL server is needed."""
import os
import shutil

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("IDENTITY_HASH_SECRET", "test-secret")
os.environ.setdefault("ADMIN_PASSWORD", "test-admin-password")
os.environ.setdefault("ADMIN_TOKEN_SECRET", "test-admin-token-secret")
os.environ["WEATHER_PROVIDER"] = "json"  # fixed sample forecasts; tests never call Open-Meteo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database.session import Base, get_db
from app.main import app


@pytest.fixture
def db():
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_headers(client):
    token = client.post("/api/admin/login", json={"password": "test-admin-password"}).json()["token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def isolated_content_dir(tmp_path, monkeypatch):
    """Content-editing tests write real files, so point them at a throwaway copy of app/data."""
    from app.services import content_service, data_loader

    tmp_dir = tmp_path / "data"
    shutil.copytree(data_loader.DATA_DIR, tmp_dir)
    monkeypatch.setattr(data_loader, "DATA_DIR", tmp_dir)
    monkeypatch.setattr(content_service, "DATA_DIR", tmp_dir)
    data_loader.load_json.cache_clear()
    yield tmp_dir
    data_loader.load_json.cache_clear()
