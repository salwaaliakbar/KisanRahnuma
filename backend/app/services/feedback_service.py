"""Helpful / not-helpful feedback, shared by the web API and the chat engine (WhatsApp buttons)."""
import uuid

from sqlalchemy.orm import Session

from app.models import FarmerConsent, Feedback
from app.repositories.feedback_repository import FeedbackRepository


class FeedbackService:
    def __init__(self, db: Session) -> None:
        self.repo = FeedbackRepository(db)

    def record(
        self,
        farmer: FarmerConsent,
        response_id: str,
        service: str,
        helpful: bool,
        session_id: uuid.UUID | None = None,
    ) -> Feedback:
        """Idempotent per response_id: a second vote on the same answer updates the first."""
        linked_farmer = farmer.farmer_id if farmer.usage_consent is True else None
        existing = self.repo.get_by_response(response_id)
        if existing:
            existing.helpful = helpful
            return existing
        return self.repo.add(
            Feedback(
                response_id=response_id,
                farmer_id=linked_farmer,
                session_id=session_id if linked_farmer else None,
                service=service,
                helpful=helpful,
            )
        )
