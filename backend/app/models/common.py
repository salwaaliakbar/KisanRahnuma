"""Shared column types and helpers."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB

# JSONB on PostgreSQL, plain JSON elsewhere (SQLite is used in tests).
JSONType = JSON().with_variant(JSONB(), "postgresql")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def as_utc(value: datetime) -> datetime:
    """SQLite returns naive datetimes; treat them as UTC so comparisons work everywhere."""
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()
