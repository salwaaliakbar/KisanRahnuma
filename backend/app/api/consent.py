import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.channels.web import CHANNEL
from app.database.session import get_db
from app.models import FarmerConsent
from app.schemas.consent import ConsentOut, ConsentUpdate
from app.services.consent_service import ConsentService

router = APIRouter(prefix="/api/consent", tags=["consent"])


def _out(farmer: FarmerConsent) -> ConsentOut:
    return ConsentOut(
        farmer_id=farmer.farmer_id,
        usage_consent=farmer.usage_consent,
        usage_consent_at=farmer.usage_consent_at,
        weekly_updates=farmer.weekly_updates,
        weekly_updates_at=farmer.weekly_updates_at,
    )


@router.get("/{client_id}", response_model=ConsentOut)
def get_consent(client_id: uuid.UUID, db: Session = Depends(get_db)) -> ConsentOut:
    farmer = ConsentService(db).find(CHANNEL, str(client_id))
    if farmer is None:
        raise HTTPException(status_code=404, detail="Farmer not found. Start a chat first.")
    return _out(farmer)


@router.post("", response_model=ConsentOut)
def update_consent(body: ConsentUpdate, db: Session = Depends(get_db)) -> ConsentOut:
    service = ConsentService(db)
    farmer = service.get_or_create(CHANNEL, str(body.client_id))
    service.update(farmer, usage_consent=body.usage_consent, weekly_updates=body.weekly_updates)
    db.commit()
    return _out(farmer)
