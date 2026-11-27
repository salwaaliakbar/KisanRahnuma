from datetime import datetime

from pydantic import BaseModel


class ServiceUsage(BaseModel):
    service: str
    label: str
    count: int


class ServiceFeedback(BaseModel):
    service: str
    label: str
    helpful: int
    not_helpful: int


class FeedbackStats(BaseModel):
    helpful: int
    not_helpful: int
    by_service: list[ServiceFeedback]


class ConsentStats(BaseModel):
    usage_allowed: int
    usage_declined: int
    usage_pending: int
    weekly_opt_in: int
    weekly_opt_out: int


class RecentInteraction(BaseModel):
    id: str
    farmer_ref: str  # first 8 chars of the anonymous id, never a phone number
    service: str
    service_label: str
    description: str
    created_at: datetime


class DashboardSummary(BaseModel):
    window_days: int
    total_farmers: int
    new_farmers: int
    active_farmers: int
    service_usage: list[ServiceUsage]
    feedback: FeedbackStats
    consent: ConsentStats
    recent_interactions: list[RecentInteraction]


class MessageUsage(BaseModel):
    """Bot messages sent this month. Only WhatsApp messages are billed, with a free monthly allowance."""

    month: str  # "2026-11"
    sent_by_channel: dict[str, int]
    whatsapp_sent: int
    whatsapp_free_limit: int
    whatsapp_free_remaining: int


class FarmerListItem(BaseModel):
    """Anonymous farmer fields only - no phone number or other identity ever appears here."""

    farmer_id: str
    channel: str
    language: str
    district: str | None
    usage_consent: bool | None
    weekly_updates: bool | None
    created_at: datetime
    updated_at: datetime


class FarmerPage(BaseModel):
    items: list[FarmerListItem]
    total: int
    offset: int
    limit: int
