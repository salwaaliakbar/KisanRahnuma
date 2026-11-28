"""Application settings.

Where each value comes from, first match wins:
  1. a real environment variable (e.g. set in a host's dashboard, where no .env file is shipped)
  2. backend/.env - the source of truth for secrets and per-deployment values
  3. the default below, so nothing has to be set for the app to start
"""
import logging
import secrets
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/.env, found the same way whatever directory the server is started from.
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

PLACEHOLDER_SECRET = "change-me-in-env"

logger = logging.getLogger("farmer_assistant")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Farmer Assistant API"
    # "development" (local) or "production" (deployed). Picks the allowed frontend origins.
    app_env: Literal["development", "production"] = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/farmer_assistant"
    # Secret used to hash channel identifiers (browser id now, WhatsApp wa_id later).
    identity_hash_secret: str = PLACEHOLDER_SECRET
    # The website allowed to call the API: FRONTEND_URL_DEV when APP_ENV=development,
    # FRONTEND_URL_PROD when APP_ENV=production. Each may list several origins, comma separated.
    frontend_url_dev: str = "http://localhost:5173,http://127.0.0.1:5173"
    frontend_url_prod: str = "https://kisanrahnuma-frontend.vercel.app"
    # Also allowed in production: Vercel's per-deployment and preview URLs, e.g.
    # https://kisanrahnuma-frontend-94u9k5pjm-salwas-projects-e922f067.vercel.app.
    # The team suffix keeps other people's Vercel projects out. Empty = off.
    frontend_url_prod_regex: str = r"https://kisanrahnuma-frontend-[a-z0-9-]+-salwas-projects-e922f067\.vercel\.app"
    # A conversation session expires after this many minutes of inactivity.
    session_timeout_minutes: int = 30
    # Language for new farmers until they choose one: "en", "ur" or "sd".
    default_language: str = "en"
    # A second tap on the same button within this many seconds is ignored (no reply sent).
    repeat_tap_seconds: int = 5
    # Inbound message ids are kept this long to drop webhook redeliveries (Meta retries for days).
    processed_message_retention_days: int = 8
    # Free WhatsApp service messages per business phone number per month (shown on the dashboard).
    whatsapp_free_messages_per_month: int = 1000

    # Admin dashboard (single shared operator password, not per-user accounts).
    admin_password: str = ""
    admin_token_secret: str = PLACEHOLDER_SECRET
    admin_token_ttl_minutes: int = 720

    # Weather source: "open_meteo" (live, free, no key) or "json" (sample data in app/data/weather.json).
    weather_provider: Literal["open_meteo", "json"] = "open_meteo"
    open_meteo_url: str = "https://api.open-meteo.com/v1/forecast"
    # A district's forecast is fetched at most once per this many minutes.
    weather_cache_minutes: int = 60
    weather_timeout_seconds: float = 10

    # WhatsApp Business Cloud API (Meta). See app/api/whatsapp_webhook.py.
    # Each setting also accepts the shorter name in brackets.
    # Access token (ACCESS_TOKEN). The test token from "API Setup" expires after 24 hours;
    # use a System User token for anything longer.
    whatsapp_access_token: str = Field("", validation_alias=AliasChoices("WHATSAPP_ACCESS_TOKEN", "ACCESS_TOKEN"))
    # The bot's phone number id (PHONE_NUMBER_ID), NOT the phone number itself.
    whatsapp_phone_number_id: str = Field("", validation_alias=AliasChoices("WHATSAPP_PHONE_NUMBER_ID", "PHONE_NUMBER_ID"))
    # Any random string; type the same value as "Verify token" in Meta's webhook settings.
    whatsapp_verify_token: str = Field("", validation_alias=AliasChoices("WHATSAPP_VERIFY_TOKEN", "VERIFY_TOKEN"))
    # App secret (App settings -> Basic): proves webhook calls really come from Meta.
    whatsapp_app_secret: str = Field("", validation_alias=AliasChoices("WHATSAPP_APP_SECRET", "APP_SECRET"))
    whatsapp_api_version: str = Field("v23.0", validation_alias=AliasChoices("WHATSAPP_API_VERSION", "API_VERSION"))

    @field_validator("database_url")
    @classmethod
    def _use_psycopg3(cls, url: str) -> str:
        # Hosted Postgres (Neon, Render...) hands out postgres:// or postgresql:// URLs, which
        # SQLAlchemy maps to psycopg2. Only psycopg v3 is installed, so name it explicitly.
        for prefix in ("postgresql://", "postgres://"):
            if url.startswith(prefix):
                return "postgresql+psycopg://" + url[len(prefix):]
        return url

    @model_validator(mode="after")
    def _warn_on_placeholder_secrets(self) -> "Settings":
        # Nothing is required: missing values fall back to the defaults above. In production,
        # a placeholder secret only logs a warning, except ADMIN_TOKEN_SECRET, which is public
        # in the source code and would let anyone forge an admin login. It falls back to a
        # random per-process secret instead (admins just log in again after a restart).
        if not self.is_production:
            return self
        if self.identity_hash_secret in ("", PLACEHOLDER_SECRET):
            logger.warning("IDENTITY_HASH_SECRET is not set; using the placeholder. Set it in .env.")
        if self.admin_token_secret in ("", PLACEHOLDER_SECRET):
            logger.warning("ADMIN_TOKEN_SECRET is not set; using a random secret until restart.")
            self.admin_token_secret = secrets.token_urlsafe(32)
        return self

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def frontend_url(self) -> str:
        return self.frontend_url_prod if self.is_production else self.frontend_url_dev

    @property
    def cors_origin_list(self) -> list[str]:
        # Browsers send the Origin without a trailing slash, so "https://x.app/" would never match.
        return [o.strip().rstrip("/") for o in self.frontend_url.split(",") if o.strip()]

    @property
    def cors_origin_regex(self) -> str | None:
        return (self.frontend_url_prod_regex or None) if self.is_production else None


@lru_cache
def get_settings() -> Settings:
    return Settings()
