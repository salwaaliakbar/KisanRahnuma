import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import FarmerConsent


class FarmerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, farmer_id: uuid.UUID) -> FarmerConsent | None:
        return self.db.get(FarmerConsent, farmer_id)

    def list_page(self, offset: int, limit: int) -> tuple[list[FarmerConsent], int]:
        """Newest first. Anonymous fields only (farmer_id, district, language, consent) - no PII."""
        total = self.db.scalar(select(func.count()).select_from(FarmerConsent)) or 0
        rows = self.db.scalars(
            select(FarmerConsent).order_by(FarmerConsent.created_at.desc()).offset(offset).limit(limit)
        ).all()
        return list(rows), total

    def get_by_ref_hash(self, ref_hash: str) -> FarmerConsent | None:
        return self.db.scalar(select(FarmerConsent).where(FarmerConsent.external_ref_hash == ref_hash))

    def create(self, channel: str, ref_hash: str, language: str) -> FarmerConsent:
        farmer = FarmerConsent(channel=channel, external_ref_hash=ref_hash, language=language)
        self.db.add(farmer)
        self.db.flush()
        return farmer
