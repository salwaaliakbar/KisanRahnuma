import uuid

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models import Feedback


class FeedbackRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def unlink_farmer(self, farmer_id: uuid.UUID) -> None:
        self.db.execute(update(Feedback).where(Feedback.farmer_id == farmer_id).values(farmer_id=None))

    def get_by_response(self, response_id: str) -> Feedback | None:
        return self.db.scalar(select(Feedback).where(Feedback.response_id == response_id))

    def add(self, feedback: Feedback) -> Feedback:
        self.db.add(feedback)
        return feedback

    def totals(self) -> dict[bool, int]:
        rows = self.db.execute(select(Feedback.helpful, func.count()).group_by(Feedback.helpful)).all()
        return {helpful: count for helpful, count in rows}

    def totals_by_service(self) -> list[tuple[str, bool, int]]:
        rows = self.db.execute(
            select(Feedback.service, Feedback.helpful, func.count()).group_by(Feedback.service, Feedback.helpful)
        ).all()
        return [(service, helpful, count) for service, helpful, count in rows]
