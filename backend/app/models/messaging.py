from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.session import Base
from app.models.common import utcnow


class ProcessedMessage(Base):
    """Inbound message ids already handled, so a redelivered webhook is not answered twice.

    WhatsApp message ids ("wamid...") encode the sender's phone number, so only a keyed
    hash of the id is stored. Rows older than a few days are pruned automatically.
    """

    __tablename__ = "processed_messages"

    channel: Mapped[str] = mapped_column(String(20), primary_key=True)
    message_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class OutboundMessageCount(Base):
    """Number of bot messages sent per channel per month (no farmer link).

    On WhatsApp every outbound message counts towards the 1,000 free messages a month,
    so this lets the dashboard show how much of the free tier has been used.
    """

    __tablename__ = "outbound_message_counts"

    channel: Mapped[str] = mapped_column(String(20), primary_key=True)
    month: Mapped[str] = mapped_column(String(7), primary_key=True)  # "2026-11"
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
