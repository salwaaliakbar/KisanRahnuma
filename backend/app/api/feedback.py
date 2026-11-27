from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.channels.web import CHANNEL
from app.database.session import get_db
from app.repositories.session_repository import SessionRepository
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.services.consent_service import ConsentService
from app.services.feedback_service import FeedbackService

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
def submit_feedback(body: FeedbackRequest, db: Session = Depends(get_db)) -> FeedbackResponse:
    farmer = ConsentService(db).find(CHANNEL, str(body.client_id))
    if farmer is None:
        raise HTTPException(status_code=404, detail="Farmer not found. Start a chat first.")
    session = SessionRepository(db).get_active(farmer.farmer_id)
    feedback = FeedbackService(db).record(
        farmer, body.response_id, body.service, body.helpful, session.id if session else None
    )
    db.commit()
    return FeedbackResponse(linked_to_farmer=feedback.farmer_id is not None)
