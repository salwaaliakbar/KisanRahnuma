from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import FarmerConsent


class FarmerStatsRepository:
    """Aggregate counts over farmer_consents. Returns numbers only, never identities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def total(self) -> int:
        return self.db.scalar(select(func.count()).select_from(FarmerConsent)) or 0

    def created_since(self, since: datetime) -> int:
        return self.db.scalar(select(func.count()).where(FarmerConsent.created_at >= since)) or 0

    def consent_breakdown(self, column) -> dict[bool | None, int]:
        rows = self.db.execute(select(column, func.count()).group_by(column)).all()
        return {value: count for value, count in rows}

    def usage_consent_breakdown(self) -> dict[bool | None, int]:
        return self.consent_breakdown(FarmerConsent.usage_consent)

    def weekly_updates_breakdown(self) -> dict[bool | None, int]:
        return self.consent_breakdown(FarmerConsent.weekly_updates)
