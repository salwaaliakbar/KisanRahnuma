import uuid
from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models import UsageLog


class UsageRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(
        self, farmer_id: uuid.UUID, session_id: uuid.UUID | None, service: str, action: str, attributes: dict
    ) -> UsageLog:
        log = UsageLog(farmer_id=farmer_id, session_id=session_id, service=service, action=action, attributes=attributes)
        self.db.add(log)
        return log

    def delete_for_farmer(self, farmer_id: uuid.UUID) -> None:
        self.db.execute(delete(UsageLog).where(UsageLog.farmer_id == farmer_id))

    def count_by_service(self, services: list[str]) -> list[tuple[str, int]]:
        rows = self.db.execute(
            select(UsageLog.service, func.count())
            .where(UsageLog.service.in_(services))
            .group_by(UsageLog.service)
            .order_by(func.count().desc())
        ).all()
        return [(service, count) for service, count in rows]

    def count_active_farmers(self, since: datetime) -> int:
        return self.db.scalar(
            select(func.count(func.distinct(UsageLog.farmer_id))).where(UsageLog.created_at >= since)
        ) or 0

    def recent(self, services: list[str], limit: int) -> list[UsageLog]:
        return list(
            self.db.scalars(
                select(UsageLog)
                .where(UsageLog.service.in_(services))
                .order_by(UsageLog.created_at.desc())
                .limit(limit)
            )
        )
