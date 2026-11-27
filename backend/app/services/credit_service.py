"""Credit awareness: ZTBL loans and Benazir Hari Card."""
from app.services.info_topics import StaticInfoService


class CreditService(StaticInfoService):
    filename = "credit_info.json"
    collection_key = "programmes"
