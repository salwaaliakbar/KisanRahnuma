import uuid
from datetime import datetime

from pydantic import BaseModel, model_validator


class ConsentUpdate(BaseModel):
    client_id: uuid.UUID
    usage_consent: bool | None = None
    weekly_updates: bool | None = None

    @model_validator(mode="after")
    def require_one(self) -> "ConsentUpdate":
        if self.usage_consent is None and self.weekly_updates is None:
            raise ValueError("Provide usage_consent and/or weekly_updates")
        return self


class ConsentOut(BaseModel):
    farmer_id: uuid.UUID
    usage_consent: bool | None
    usage_consent_at: datetime | None
    weekly_updates: bool | None
    weekly_updates_at: datetime | None
