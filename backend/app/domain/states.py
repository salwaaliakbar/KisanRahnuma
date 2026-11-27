from enum import StrEnum


class ConversationState(StrEnum):
    CHOOSE_LANGUAGE = "CHOOSE_LANGUAGE"
    CONSENT = "CONSENT"  # usage + weekly-updates permissions, asked in one message
    MAIN_MENU = "MAIN_MENU"
    CHOOSE_DISTRICT = "CHOOSE_DISTRICT"
    WEATHER_DISTRICT = "WEATHER_DISTRICT"
    CROP_SELECT = "CROP_SELECT"
    CROP_DISTRICT = "CROP_DISTRICT"
    CREDIT_MENU = "CREDIT_MENU"
    CERT_MENU = "CERT_MENU"
    ASK_ANYTHING = "ASK_ANYTHING"


class Service(StrEnum):
    """Service names used in usage logs, feedback and the dashboard."""

    ONBOARDING = "onboarding"
    MENU = "menu"
    WEATHER = "weather"
    CROP_RATES = "crop_rates"
    CREDIT = "credit"
    CERTIFICATIONS = "certifications"
    ASK_ANYTHING = "ask_anything"
