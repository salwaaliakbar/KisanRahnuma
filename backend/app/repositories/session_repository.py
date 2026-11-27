import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ConversationSession


class SessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_active(self, farmer_id: uuid.UUID) -> ConversationSession | None:
        return self.db.scalar(
            select(ConversationSession)
            .where(ConversationSession.farmer_id == farmer_id, ConversationSession.is_active.is_(True))
            .order_by(ConversationSession.last_activity_at.desc())
            .limit(1)
        )

    def create(self, farmer_id: uuid.UUID, channel: str, state: str) -> ConversationSession:
        session = ConversationSession(farmer_id=farmer_id, channel=channel, state=state, context={})
        self.db.add(session)
        self.db.flush()
        return session
