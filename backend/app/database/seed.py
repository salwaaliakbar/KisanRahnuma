"""Seed demo activity data for the dashboard: farmers, sessions, usage logs, feedback and
outbound WhatsApp message counts.

    python -m app.database.seed            # adds demo data (skips if demo data exists)
    python -m app.database.seed --reset    # DROP all tables (real data too), recreate, then seed

Chatbot CONTENT (weather districts, crop rates, credit, certifications, knowledge base) is not
in the database: it lives in app/data/*.json, is read at startup and is shared through git.
This script only fakes ACTIVITY, and takes topic/crop/district ids from those files so it
never goes out of date. processed_messages (webhook dedupe ids) is left empty on purpose.
"""
import argparse
from collections import Counter
import random
import uuid
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.init_db import init_db
from app.database.session import SessionLocal
from app.domain.states import ConversationState, Service
from app.models import ConversationSession, FarmerConsent, Feedback, OutboundMessageCount, UsageLog
from app.models.common import utcnow
from app.services.certification_service import CertificationService
from app.services.consent_service import hash_external_ref
from app.services.credit_service import CreditService
from app.services.crop_service import CropService
from app.services.knowledge_service import KnowledgeService
from app.services.weather_service import JsonWeatherProvider

DEMO_CHANNEL = "demo"
LANGUAGES = (["sd"] * 5) + (["ur"] * 3) + (["en"] * 2)  # mostly Sindhi, as expected in Upper Sindh
ONBOARDING_MESSAGES = 4  # language, district, consent, main menu


def _content_ids() -> dict[str, list]:
    """Ids from app/data/*.json, so demo activity always refers to real content."""
    return {
        "districts": [d.id for d in JsonWeatherProvider().districts()],
        "crops": [c.id for c in CropService().crops()],
        "credit": [t.id for t in CreditService().topics()],
        "certifications": [t.id for t in CertificationService().topics()],
        # None = an unanswered question
        "knowledge": [e[0]["id"] for e in KnowledgeService()._entries] + [None, None],
    }


def _services(ids: dict[str, list]) -> dict:
    # service -> (relative popularity, action, attribute generator)
    return {
        Service.WEATHER: (30, "forecast_viewed", lambda r: {"district": r.choice(ids["districts"])}),
        Service.CROP_RATES: (34, "rate_viewed", lambda r: {"crop": r.choice(ids["crops"]), "district": r.choice(ids["districts"])}),
        Service.CREDIT: (12, "info_viewed", lambda r: {"topic": r.choice(ids["credit"])}),
        Service.CERTIFICATIONS: (8, "info_viewed", lambda r: {"topic": r.choice(ids["certifications"])}),
        Service.ASK_ANYTHING: (16, None, None),
    }


def seed(db: Session, farmers: int = 42, days: int = 30, rng_seed: int = 7) -> int:
    existing = db.scalar(select(func.count()).where(FarmerConsent.channel == DEMO_CHANNEL)) or 0
    if existing:
        print(f"Demo data already present ({existing} demo farmers). Use --reset to recreate.")
        return 0

    rng = random.Random(rng_seed)
    secret = get_settings().identity_hash_secret
    now = utcnow()
    ids = _content_ids()
    SERVICES = _services(ids)
    services, weights = zip(*[(s, w[0]) for s, w in SERVICES.items()])
    outbound = Counter()  # "YYYY-MM" -> bot messages sent (one per farmer action)

    for i in range(farmers):
        joined = now - timedelta(days=rng.uniform(0, days), hours=rng.uniform(0, 12))
        allowed = rng.random() < 0.8
        farmer = FarmerConsent(
            channel=DEMO_CHANNEL,
            external_ref_hash=hash_external_ref(DEMO_CHANNEL, f"demo-farmer-{i}", secret),
            language=rng.choice(LANGUAGES),
            district=rng.choice(ids["districts"]),
            usage_consent=allowed,
            usage_consent_at=joined,
            weekly_updates=rng.random() < 0.55,
            weekly_updates_at=joined,
            created_at=joined,
            updated_at=joined,
        )
        db.add(farmer)
        db.flush()
        outbound[joined.strftime("%Y-%m")] += ONBOARDING_MESSAGES

        for _ in range(rng.randint(1, 4)):
            started = joined + timedelta(hours=rng.uniform(0, max((now - joined).total_seconds() / 3600, 0.1)))
            session = ConversationSession(
                farmer_id=farmer.farmer_id,
                channel=DEMO_CHANNEL,
                state=ConversationState.MAIN_MENU.value,
                context={},
                is_active=False,
                started_at=started,
                last_activity_at=started + timedelta(minutes=rng.randint(2, 15)),
            )
            db.add(session)
            db.flush()

            for step in range(rng.randint(1, 4)):
                at = started + timedelta(minutes=step * 2 + 1)
                service = rng.choices(services, weights=weights)[0]
                _, action, attrs = SERVICES[service]
                outbound[at.strftime("%Y-%m")] += 1
                if service == Service.ASK_ANYTHING:
                    topic = rng.choice(ids["knowledge"])
                    action, attributes = ("question_answered", {"topic": topic}) if topic else ("question_unanswered", {})
                else:
                    attributes = attrs(rng)
                if allowed:  # usage is recorded only with consent
                    db.add(UsageLog(farmer_id=farmer.farmer_id, session_id=session.id, service=service.value,
                                    action=action, attributes=attributes, created_at=at))
                if rng.random() < 0.6:
                    helpful = rng.random() < (0.45 if action == "question_unanswered" else 0.82)
                    db.add(Feedback(
                        response_id=uuid.uuid4().hex,
                        farmer_id=farmer.farmer_id if allowed else None,
                        session_id=session.id if allowed else None,
                        service=service.value,
                        helpful=helpful,
                        created_at=at,
                    ))
    for month, count in outbound.items():
        db.add(OutboundMessageCount(channel=DEMO_CHANNEL, month=month, count=count))
    db.commit()
    return farmers


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="drop and recreate tables before seeding")
    args = parser.parse_args()
    init_db(reset=args.reset)
    with SessionLocal() as db:
        created = seed(db)
    if created:
        print(f"Seeded {created} demo farmers with sessions, usage logs, feedback and message counts.")
