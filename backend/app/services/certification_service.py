"""Certification awareness: green, organic and other schemes."""
from app.services.info_topics import StaticInfoService


class CertificationService(StaticInfoService):
    filename = "certifications.json"
    collection_key = "certifications"
