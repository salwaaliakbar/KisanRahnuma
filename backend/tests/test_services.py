from app.services.certification_service import CertificationService
from app.services.credit_service import CreditService
from app.services.crop_service import CropService
from app.services.knowledge_service import KnowledgeService
from app.services.weather_service import DayForecast, WeatherService, farm_advice


def test_weather_report_has_three_days_and_advice():
    report = WeatherService().get_report("khairpur")
    assert report is not None
    assert len(report.days) == 3
    assert "advice_rain" in report.advice_keys  # Khairpur dummy data has rain


def test_weather_unknown_district():
    assert WeatherService().get_report("lahore") is None


def test_farm_advice_default_when_calm():
    from datetime import date

    calm = [DayForecast(date.today(), "Sunny", 15, 28, 0, 40, 8)]
    assert farm_advice(calm) == ["advice_default"]


def test_crop_report_contains_rate_trend_and_range():
    report = CropService().get_report("wheat", "sukkur")
    assert report is not None
    assert report.rate > 0 and report.source and report.date
    assert report.expected.low < report.expected.high
    assert report.trend.summer_avg > 0


def test_info_services_load_topics():
    assert {t.id for t in CreditService().topics()} == {
        "zarkhez", "hari_card", "sindh_bank", "pm_youth", "ztbl", "interest_free", "other", "compare", "before_borrowing"
    }
    assert [t.id for t in CertificationService().topics()] == [
        "cotton", "dates", "mango", "rice", "wheat", "other", "organic"
    ]
    assert CertificationService().intro() is not None
    assert CreditService().intro() is None


def test_certification_answers_fit_one_whatsapp_message():
    from app.domain.messages import MAX_INTERACTIVE_TEXT, MAX_OPTIONS
    from app.domain.states import Service
    from app.i18n import SUPPORTED_LANGUAGES
    from app.services.presenters import info_answer

    topics = CertificationService().topics()
    assert len(topics) + 1 <= MAX_OPTIONS  # + Home: still one WhatsApp list
    for topic in topics:
        for lang in SUPPORTED_LANGUAGES:
            text = info_answer(topic, Service.CERTIFICATIONS, lang).text
            assert len(text) <= MAX_INTERACTIVE_TEXT, (topic.id, lang, len(text))


def test_certification_menu_with_intro_fits_one_whatsapp_message():
    from app.domain.messages import MAX_INTERACTIVE_TEXT
    from app.i18n import SUPPORTED_LANGUAGES
    from app.services.conversation_service import ConversationService
    from app.services.presenters import info_menu

    service = CertificationService()
    for lang in SUPPORTED_LANGUAGES:
        options = ConversationService._topic_options("cert", service.topics(), lang)
        menu = info_menu("cert_menu", service.intro(), options, lang)
        assert len(menu.text) <= MAX_INTERACTIVE_TEXT, (lang, len(menu.text))
        assert "{intro}" not in menu.text


def test_knowledge_search_matches_and_falls_back():
    kb = KnowledgeService()
    assert kb.search("How to control pink bollworm?").topic_id == "cotton_pink_bollworm"
    assert kb.search("When should I sow wheat").topic_id == "wheat_sowing_time"
    assert kb.search("when to plant cotton").topic_id == "cotton_sowing"
    assert kb.search("what is the price of gold") is None
    assert kb.search("") is None


def test_seed_fills_every_activity_table_with_real_content_ids(db):
    from sqlalchemy import func, select

    from app.database.seed import _content_ids, seed
    from app.models import ConversationSession, FarmerConsent, Feedback, OutboundMessageCount, UsageLog

    assert seed(db, farmers=15) == 15
    for model in (FarmerConsent, ConversationSession, UsageLog, Feedback, OutboundMessageCount):
        assert db.scalar(select(func.count()).select_from(model)) > 0, model.__tablename__

    ids = _content_ids()
    farmers = db.scalars(select(FarmerConsent)).all()
    assert all(f.district in ids["districts"] and f.language in ("en", "ur", "sd") for f in farmers)
    for log in db.scalars(select(UsageLog)).all():
        topic = (log.attributes or {}).get("topic")
        if log.service == "certifications":
            assert topic in ids["certifications"]
        elif log.service == "credit":
            assert topic in ids["credit"]

    assert seed(db) == 0  # running it again adds nothing
