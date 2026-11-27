from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.models import OutboundMessageCount, ProcessedMessage


class ProcessedMessageRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def claim(self, channel: str, message_hash: str) -> bool:
        """Record an inbound message id. False if it was already handled (a redelivery).

        Two concurrent deliveries of the same id both pass the check, but the primary key
        makes the second commit fail, so it rolls back before any reply is sent.
        """
        exists = self.db.scalar(
            select(ProcessedMessage.message_hash).where(
                ProcessedMessage.channel == channel, ProcessedMessage.message_hash == message_hash
            )
        )
        if exists:
            return False
        self.db.add(ProcessedMessage(channel=channel, message_hash=message_hash))
        return True

    def prune(self, older_than: datetime) -> None:
        self.db.execute(delete(ProcessedMessage).where(ProcessedMessage.created_at < older_than))


class OutboundCountRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, channel: str, month: str, count: int) -> None:
        # Atomic increment, so concurrent requests do not lose counts.
        result = self.db.execute(
            update(OutboundMessageCount)
            .where(OutboundMessageCount.channel == channel, OutboundMessageCount.month == month)
            .values(count=OutboundMessageCount.count + count)
        )
        if result.rowcount == 0:
            self.db.add(OutboundMessageCount(channel=channel, month=month, count=count))
            self.db.flush()

    def for_month(self, month: str) -> dict[str, int]:
        rows = self.db.execute(
            select(OutboundMessageCount.channel, OutboundMessageCount.count).where(OutboundMessageCount.month == month)
        ).all()
        return {channel: count for channel, count in rows}
