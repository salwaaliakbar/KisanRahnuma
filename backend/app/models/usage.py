import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.models.common import JSONType, new_uuid, utcnow


class UsageLog(Base):
    """Anonymous usage event. Rows are written ONLY for farmers with usage_consent = true.

    `attributes` holds structured selections (district, crop, knowledge topic id),
    never the farmer's free-text message.
    """

    __tablename__ = "usage_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    farmer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("farmer_consents.farmer_id", ondelete="CASCADE"), index=True, nullable=False
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("conversation_sessions.id", ondelete="SET NULL"), nullable=True
    )
    service: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(60), nullable=False)
    attributes: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
