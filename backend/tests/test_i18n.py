"""Multilingual behaviour: English, Urdu and Sindhi catalogues, data and conversation flows."""
import string

import pytest

from app.i18n import CATALOGUES, SUPPORTED_LANGUAGES, pick
from app.services.certification_service import CertificationService
from app.services.conversation_service import localized_option
from app.services.credit_service import CreditService
from app.services.crop_service import CropService
from app.services.data_loader import load_json
from app.services.knowledge_service import KnowledgeService
from app.services.text_utils import normalize
from app.services.weather_service import WeatherService
from tests.test_conversation import Farmer


def placeholders(template: str) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(template) if name}


@pytest.mark.parametrize("lang", ["ur", "sd"])
def test_catalogue_matches_english(lang):
    en, other = CATALOGUES["en"], CATALOGUES[lang]
    assert set(other) == set(en), "missing or extra keys"
    for key, template in en.items():
        assert placeholders(other[key]) == placeholders(template), key


def _localized_values(node, path="$"):
    """Yield every {en, ur, sd} object in a data file."""
    if isinstance(node, dict):
        if "en" in node and all(isinstance(v, str) for v in node.values()):
            yield path, node
            return
        for key, value in node.items():
            yield from _localized_values(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from _localized_values(value, f"{path}[{i}]")


@pytest.mark.parametrize(
    "filename", ["weather.json", "crop_rates.json", "credit_info.json", "certifications.json", "knowledge_base.json"]
)
def test_data_files_are_fully_translated(filename):
    for path, value in _localized_values(load_json(filename)):
        if path.endswith(".keywords"):
            continue
        assert set(value) == set(SUPPORTED_LANGUAGES), f"{filename} {path}"
        assert all(text.strip() for text in value.values()), f"{filename} {path}"


@pytest.mark.parametrize("lang", SUPPORTED_LANGUAGES)
def test_every_option_label_fits_whatsapp(lang):
    # Option() raises if a label is longer than WhatsApp allows.
    for d in WeatherService().districts() + CropService().districts():
        localized_option("district", d.name, lang)
    for c in CropService().crops():
        localized_option("crop", c.name, lang)
    for topic in CreditService().topics() + CertificationService().topics():
        localized_option("topic", topic.label, lang)


def test_normalize_folds_script_variants():
    assert normalize("جي") == normalize("جی")  # Arabic vs Urdu yeh
    assert normalize("نہ") == normalize("نه")  # Urdu heh goal vs heh
    assert normalize("لُڪ") == normalize("لڪ")  # diacritics dropped
    assert normalize("۲") == "2"


def test_urdu_onboarding_and_weather(db):
    f = Farmer(db)
    f.say("السلام علیکم")
    r = f.say(option_id="lang:ur")
    assert r.state == "CHOOSE_DISTRICT" and r.language == "ur"
    r = f.say("سکھر")  # district typed in Urdu
    assert r.state == "CONSENT"
    assert r.messages[0].options[0].label == "دونوں کی اجازت"
    r = f.say("نہیں")  # typed Urdu no: neither permission
    assert r.state == "MAIN_MENU"
    assert r.messages[0].options[0].label == "موسم"

    r = f.say("1")  # Weather answers at once for the district chosen at onboarding
    text = r.messages[0].text
    assert "سکھر" in text and "زرعی مشورہ" in text
    assert "Sukkur" not in text


def test_sindhi_crop_rates_accept_names_in_any_language(db):
    f = Farmer(db)
    f.onboard(lang="sd")
    f.say(option_id="menu:crops")
    r = f.say("ڪڻڪ")  # wheat in Sindhi
    assert r.state == "CROP_DISTRICT"
    r = f.say("Ghotki")  # district in English still works
    text = r.messages[0].text
    assert "ڪڻڪ جو اگهه: گهوٽڪي" in text and "رپيا" in text


def test_switch_language_mid_conversation(db):
    f = Farmer(db)
    f.onboard()
    f.say(option_id="menu:weather")
    r = f.say("urdu")
    assert r.state == "MAIN_MENU" and r.language == "ur"
    assert "زبان اردو کر دی گئی ہے" in r.messages[0].text

    r = f.say(option_id="menu:language")
    assert r.state == "CHOOSE_LANGUAGE"
    assert [o.id for o in r.messages[0].options] == ["lang:en", "lang:ur", "lang:sd", "nav:home"]
    r = f.say("3")  # Sindhi
    assert r.language == "sd" and "ٻولي سنڌي" in r.messages[0].text

    r = f.say(option_id="lang:en")
    assert r.language == "en" and "Language changed to English" in r.messages[0].text


def test_switching_language_during_consent_keeps_the_question(db):
    f = Farmer(db)
    f.say("hi")
    f.say(option_id="lang:en")
    f.say(option_id="district:sukkur")
    r = f.say(option_id="lang:sd")
    assert r.state == "CONSENT"
    assert "ٻه اجازتون" in r.messages[0].text


def test_onboarding_language_question_is_reasked(db):
    f = Farmer(db)
    f.say("hi")
    r = f.say("what?")
    assert r.state == "CHOOSE_LANGUAGE"


@pytest.mark.parametrize(
    "question, topic",
    [
        ("گندم کب کاشت کریں؟", "wheat_sowing_time"),
        ("گندم کے لیے کتنی یوریا", "wheat_fertilizer"),
        ("کپاس میں گلابی سنڈی", "cotton_pink_bollworm"),
        ("ڪڻڪ ڪڏهن پوکجي؟", "wheat_sowing_time"),
        ("ڪڻڪ کي ڪيترو ڀاڻ گهرجي", "wheat_fertilizer"),
        ("ڪپهه ۾ اڇي مک", "cotton_whitefly"),
        ("مٽي جي جاچ ڪيئن ڪجي", "soil_testing"),
    ],
)
def test_knowledge_search_in_urdu_and_sindhi(question, topic):
    result = KnowledgeService().search(question)
    assert result is not None and result.topic_id == topic


def test_answer_is_in_farmers_language_whatever_language_they_type(db):
    f = Farmer(db)
    f.onboard(lang="ur")
    r = f.say("When should I sow wheat?")
    expected = pick(KnowledgeService().search("wheat sowing").answer, "ur")
    assert expected in r.messages[0].text
