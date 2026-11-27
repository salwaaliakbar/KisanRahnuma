"""Application settings, loaded from environment variables / backend/.env."""
from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Farmer Assistant API"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/farmer_assistant"
    # Secret used to hash channel identifiers (browser id now, WhatsApp wa_id later).
    identity_hash_secret: str = "change-me-in-env"
    # Comma-separated list of allowed frontend origins.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
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
    admin_token_secret: str = "change-me-in-env"
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

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
