from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.session import get_db
from app.models.common import utcnow
from app.repositories.message_repository import OutboundCountRepository
from app.schemas.dashboard import DashboardSummary, MessageUsage
from app.services.admin_auth import require_admin
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"], dependencies=[Depends(require_admin)])


@router.get("/summary", response_model=DashboardSummary)
def summary(days: int = Query(default=7, ge=1, le=90), db: Session = Depends(get_db)) -> DashboardSummary:
    return DashboardService(db).summary(window_days=days)


@router.get("/messages", response_model=MessageUsage)
def message_usage(db: Session = Depends(get_db)) -> MessageUsage:
    """How much of this month's free WhatsApp allowance the bot's replies have used."""
    month = utcnow().strftime("%Y-%m")
    counts = OutboundCountRepository(db).for_month(month)
    limit = get_settings().whatsapp_free_messages_per_month
    sent = counts.get("whatsapp", 0)
    return MessageUsage(
        month=month,
        sent_by_channel=counts,
        whatsapp_sent=sent,
        whatsapp_free_limit=limit,
        whatsapp_free_remaining=max(limit - sent, 0),
    )
