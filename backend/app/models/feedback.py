import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.models.common import new_uuid, utcnow


class Feedback(Base):
    """Helpful / not-helpful vote on one assistant answer.

    Always stored (it is an explicit action), but `farmer_id` is only filled in
    when the farmer consented to usage recording.
    """

    __tablename__ = "feedback"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=new_uuid)
    response_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    farmer_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("farmer_consents.farmer_id", ondelete="SET NULL"), nullable=True
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("conversation_sessions.id", ondelete="SET NULL"), nullable=True
    )
    service: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    helpful: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
