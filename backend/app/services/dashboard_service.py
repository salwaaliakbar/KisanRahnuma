"""Aggregated, anonymous numbers for the development dashboard."""
from datetime import timedelta

from sqlalchemy.orm import Session

from app.domain.states import Service
from app.models.common import utcnow
from app.repositories.dashboard_repository import FarmerStatsRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.usage_repository import UsageRepository
from app.schemas.dashboard import (
    ConsentStats,
    DashboardSummary,
    FeedbackStats,
    RecentInteraction,
    ServiceFeedback,
    ServiceUsage,
)

FEATURE_SERVICES = [
    Service.WEATHER,
    Service.CROP_RATES,
    Service.CREDIT,
    Service.CERTIFICATIONS,
    Service.ASK_ANYTHING,
]
SERVICE_LABELS = {
    Service.WEATHER: "Weather",
    Service.CROP_RATES: "Crop Rates",
    Service.CREDIT: "Credit Information",
    Service.CERTIFICATIONS: "Certifications",
    Service.ASK_ANYTHING: "Ask Anything",
}


def describe(service: str, action: str, attributes: dict) -> str:
    details = ", ".join(str(v).replace("_", " ").title() for v in attributes.values())
    readable = action.replace("_", " ").capitalize()
    return f"{readable}: {details}" if details else readable


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.farmers = FarmerStatsRepository(db)
        self.usage = UsageRepository(db)
        self.feedback = FeedbackRepository(db)

    def summary(self, window_days: int = 7, recent_limit: int = 12) -> DashboardSummary:
        since = utcnow() - timedelta(days=window_days)
        services = [s.value for s in FEATURE_SERVICES]

        counts = dict(self.usage.count_by_service(services))
        usage = sorted(
            (ServiceUsage(service=s.value, label=SERVICE_LABELS[s], count=counts.get(s.value, 0)) for s in FEATURE_SERVICES),
            key=lambda u: u.count,
            reverse=True,
        )

        totals = self.feedback.totals()
        per_service: dict[str, ServiceFeedback] = {}
        for service, helpful, count in self.feedback.totals_by_service():
            label = SERVICE_LABELS.get(Service(service), service) if service in services else service
            item = per_service.setdefault(service, ServiceFeedback(service=service, label=label, helpful=0, not_helpful=0))
            if helpful:
                item.helpful += count
            else:
                item.not_helpful += count

        usage_consent = self.farmers.usage_consent_breakdown()
        weekly = self.farmers.weekly_updates_breakdown()

        recent = [
            RecentInteraction(
                id=str(log.id),
                farmer_ref=str(log.farmer_id)[:8],
                service=log.service,
                service_label=SERVICE_LABELS.get(Service(log.service), log.service),
                description=describe(log.service, log.action, log.attributes or {}),
                created_at=log.created_at,
            )
            for log in self.usage.recent(services, recent_limit)
        ]

        return DashboardSummary(
            window_days=window_days,
            total_farmers=self.farmers.total(),
            new_farmers=self.farmers.created_since(since),
            active_farmers=self.usage.count_active_farmers(since),
            service_usage=usage,
            feedback=FeedbackStats(
                helpful=totals.get(True, 0),
                not_helpful=totals.get(False, 0),
                by_service=sorted(per_service.values(), key=lambda f: f.helpful + f.not_helpful, reverse=True),
            ),
            consent=ConsentStats(
                usage_allowed=usage_consent.get(True, 0),
                usage_declined=usage_consent.get(False, 0),
                usage_pending=usage_consent.get(None, 0),
                weekly_opt_in=weekly.get(True, 0),
                weekly_opt_out=weekly.get(False, 0),
            ),
            recent_interactions=recent,
        )
