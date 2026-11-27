import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.models.common import JSONType, new_uuid, utcnow


class ConversationSession(Base):
    """Conversation state for multi-step flows (e.g. crop -> district).

    `state` is a ConversationState value; `context` holds step data such as the chosen crop.
    """

    __tablename__ = "conversation_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    farmer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("farmer_consents.farmer_id", ondelete="CASCADE"), index=True, nullable=False
    )
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    state: Mapped[str] = mapped_column(String(40), nullable=False)
    context: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    # Last tapped option and when, to ignore accidental double taps (each reply costs money).
    last_option_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    last_option_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
