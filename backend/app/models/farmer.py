import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.models.common import new_uuid, utcnow


class FarmerConsent(Base):
    """One row per farmer. `farmer_id` is the random anonymous identity used everywhere else.

    The channel identifier (browser id, WhatsApp number) is stored only as a keyed hash,
    so the raw phone number never appears in this or any analytics table.
    Usage-recording consent and weekly-update preference are separate, independent fields.
    """

    __tablename__ = "farmer_consents"

    farmer_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    external_ref_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    # The farmer's district id (e.g. "sukkur"), a preference like language. Remembered so
    # weather and crop rates skip the district question. Never a precise location.
    district: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # None = not answered yet.
    usage_consent: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    usage_consent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    weekly_updates: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    weekly_updates_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    @property
    def consent_complete(self) -> bool:
        return self.usage_consent is not None and self.weekly_updates is not None
