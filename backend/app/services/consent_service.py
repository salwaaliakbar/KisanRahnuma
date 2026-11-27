"""Anonymous farmer identity and consent preferences.

Channel identifiers (a browser id today, a WhatsApp number later) are converted to an
HMAC-SHA256 hash with a server-side secret. The raw identifier is never stored, but the
same farmer always maps to the same anonymous farmer_id.
"""
import hashlib
import hmac

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models import FarmerConsent
from app.models.common import utcnow
from app.repositories.farmer_repository import FarmerRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.usage_repository import UsageRepository


def hash_external_ref(channel: str, external_ref: str, secret: str) -> str:
    message = f"{channel}:{external_ref}".encode()
    return hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()


class ConsentService:
    def __init__(self, db: Session, settings: Settings | None = None) -> None:
        self.db = db
        self.settings = settings or get_settings()
        self.farmers = FarmerRepository(db)

    def _hash(self, channel: str, external_ref: str) -> str:
        return hash_external_ref(channel, external_ref, self.settings.identity_hash_secret)

    def find(self, channel: str, external_ref: str) -> FarmerConsent | None:
        return self.farmers.get_by_ref_hash(self._hash(channel, external_ref))

    def get_or_create(self, channel: str, external_ref: str) -> FarmerConsent:
        ref_hash = self._hash(channel, external_ref)
        farmer = self.farmers.get_by_ref_hash(ref_hash)
        if farmer is None:
            farmer = self.farmers.create(channel, ref_hash, self.settings.default_language)
        return farmer

    def set_usage_consent(self, farmer: FarmerConsent, allowed: bool) -> None:
        withdrawn = farmer.usage_consent is True and not allowed
        farmer.usage_consent = allowed
        farmer.usage_consent_at = utcnow()
        if withdrawn:
            # Respect withdrawal: remove recorded usage and unlink earlier feedback.
            UsageRepository(self.db).delete_for_farmer(farmer.farmer_id)
            FeedbackRepository(self.db).unlink_farmer(farmer.farmer_id)

    def set_weekly_updates(self, farmer: FarmerConsent, wanted: bool) -> None:
        farmer.weekly_updates = wanted
        farmer.weekly_updates_at = utcnow()

    def update(
        self, farmer: FarmerConsent, usage_consent: bool | None = None, weekly_updates: bool | None = None
    ) -> FarmerConsent:
        if usage_consent is not None:
            self.set_usage_consent(farmer, usage_consent)
        if weekly_updates is not None:
            self.set_weekly_updates(farmer, weekly_updates)
        return farmer
