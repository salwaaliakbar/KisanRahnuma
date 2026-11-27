"""Records anonymous usage events, but only for farmers who consented."""
import uuid

from sqlalchemy.orm import Session

from app.models import FarmerConsent
from app.repositories.usage_repository import UsageRepository


class UsageService:
    def __init__(self, db: Session) -> None:
        self.repo = UsageRepository(db)

    def record(
        self,
        farmer: FarmerConsent,
        session_id: uuid.UUID | None,
        service: str,
        action: str,
        attributes: dict | None = None,
    ) -> bool:
        """Returns True if the event was stored."""
        if farmer.usage_consent is not True:
            return False
        self.repo.add(farmer.farmer_id, session_id, service, action, attributes or {})
        return True
