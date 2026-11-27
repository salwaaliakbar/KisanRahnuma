"""Conversation engine tests, called directly (no HTTP) to prove it is channel-independent."""
import pytest
from sqlalchemy import func, select

from app.domain.messages import InboundKind, InboundMessage, feedback_option_id
from app.models import FarmerConsent, Feedback, UsageLog
from app.services.conversation_service import ConversationService


class Farmer:
    """Helper that chats with the engine as one farmer on one channel."""

    def __init__(self, db, ref="farmer-1", channel="web"):
        self.db, self.ref, self.channel = db, ref, channel

    def say(self, text=None, option_id=None, kind=InboundKind.TEXT, message_id=None):
        if option_id and kind == InboundKind.TEXT:
            kind = InboundKind.OPTION
        msg = InboundMessage(
            channel=self.channel, external_ref=self.ref, kind=kind, text=text, option_id=option_id, message_id=message_id
        )
        return ConversationService(self.db).handle(msg)

    def onboard(self, usage=True, weekly=True, lang="en", district="sukkur"):
        self.say("hi")
        self.say(option_id=f"lang:{lang}")
        self.say(option_id=f"district:{district}")
        choice = "none" if not usage else ("both" if weekly else "usage")
        return self.say(option_id=f"consent:{choice}")

    def record(self):
        return self.db.scalar(select(FarmerConsent).where(FarmerConsent.channel == self.channel))


def usage_count(db):
    return db.scalar(select(func.count()).select_from(UsageLog))


def test_new_farmer_picks_language_then_consent_then_sees_menu(db):
    f = Farmer(db)
    r = f.say("Hello")
    assert r.state == "CHOOSE_LANGUAGE"
    assert [o.label for o in r.messages[0].options] == ["English", "اردو", "سنڌي"]

    r = f.say("1")  # English
    assert r.state == "CHOOSE_DISTRICT"
    assert "Welcome" in r.messages[0].text
    assert [o.id for o in r.messages[0].options] == ["district:sukkur", "district:khairpur", "district:ghotki"]

    r = f.say("2")  # Khairpur
    assert r.state == "CONSENT"  # both permissions in ONE message
    assert [o.label for o in r.messages[0].options] == ["Yes to both", "Only 1 (no updates)", "No to both"]

    r = f.say(option_id="consent:usage")
    assert r.state == "MAIN_MENU"
    assert len(r.messages[0].options) == 7  # 5 services + My district + Language
    farmer = f.record()
    assert farmer.usage_consent is True and farmer.weekly_updates is False
    assert farmer.district == "khairpur"


def test_onboarding_district_is_reasked_on_unclear_answer(db):
    f = Farmer(db)
    f.say("hi")
    f.say(option_id="lang:en")
    r = f.say("what?")
    assert r.state == "CHOOSE_DISTRICT" and f.record().district is None


@pytest.mark.parametrize("answer, usage, weekly", [("yes", True, True), ("no", False, False), ("3", False, False)])
def test_consent_can_be_typed(db, answer, usage, weekly):
    f = Farmer(db)
    f.say("hi")
    f.say(option_id="lang:en")
    f.say(option_id="district:sukkur")
    assert f.say(answer).state == "MAIN_MENU"
    assert (f.record().usage_consent, f.record().weekly_updates) == (usage, weekly)


def test_onboarding_takes_four_messages(db):
    f = Farmer(db)
    replies = [f.say("hi"), f.say(option_id="lang:en"), f.say(option_id="district:ghotki"), f.say(option_id="consent:both")]
    assert sum(len(r.messages) for r in replies) == 4
    assert replies[-1].state == "MAIN_MENU"


def test_consent_question_is_reasked_on_unclear_answer(db):
    f = Farmer(db)
    f.say("hi")
    f.say(option_id="lang:en")
    f.say(option_id="district:sukkur")
    r = f.say("what is this?")
    assert r.state == "CONSENT"
    assert "Please tap one of the buttons" in r.messages[0].text


def test_returning_farmer_goes_straight_to_menu(db):
    f = Farmer(db)
    f.onboard()
    r = f.say("hi")
    assert r.state == "MAIN_MENU"


def test_weather_flow(db):
    f = Farmer(db)
    f.onboard()
    r = f.say(option_id="menu:weather")
    assert r.state == "WEATHER_DISTRICT"
    r = f.say("Sukkur")
    msg = r.messages[0]
    assert "Sukkur" in msg.text and "Farm advice" in msg.text
    assert msg.feedback is True and msg.service == "weather"
    # State is kept so another district can be typed directly.
    assert "Ghotki" in f.say("ghotki").messages[0].text


def test_district_is_remembered_for_weather_and_crop_rates(db):
    f = Farmer(db)
    f.onboard(district="khairpur")

    # Weather answers straight from the menu: no district question.
    r = f.say(option_id="menu:weather")
    assert "Khairpur" in r.messages[0].text and r.messages[0].feedback is True

    # Crop rates: menu -> crop -> answer (the district step is skipped).
    f.say("home")
    r = f.say(option_id="menu:crops")
    assert "Khairpur" in r.messages[0].text
    r = f.say(option_id="crop:wheat")
    assert "Wheat rate: Khairpur" in r.messages[0].text


def test_my_district_menu_changes_the_saved_district(db):
    f = Farmer(db)
    f.onboard()
    r = f.say(option_id="menu:district")
    assert r.state == "CHOOSE_DISTRICT"
    r = f.say(option_id="district:ghotki")
    assert r.state == "MAIN_MENU" and "Ghotki" in r.messages[0].text
    assert f.record().district == "ghotki"
    f.say(option_id="menu:crops")
    assert "rate: Ghotki" in f.say("cotton").messages[0].text


def test_crop_rate_flow_with_typed_numbers(db):
    f = Farmer(db)
    f.onboard()
    f.say("2")  # Crop Rates
    r = f.say("cotton")
    assert r.state == "CROP_DISTRICT"
    r = f.say("3")  # Ghotki
    text = r.messages[0].text
    assert "Cotton" in text and "Ghotki" in text
    assert "Seasonal trend" in text and "Expected price" in text and "Source" in text


def test_credit_and_certification_flows(db):
    f = Farmer(db)
    f.onboard()
    f.say(option_id="menu:credit")
    assert "Benazir Hari Card" in f.say("benazir").messages[0].text
    text = f.say("zarkhez").messages[0].text
    assert "Rs 1,200" in text and "do not recommend any one bank" in text
    f.say("home")
    menu = f.say(option_id="menu:certifications").messages[0]
    assert "Before you spend money" in menu.text  # the general intro comes with the crop list
    assert [o.id for o in menu.options][:2] == ["cert:cotton", "cert:dates"]
    organic = f.say(option_id="cert:organic").messages[0].text
    assert "Organic certification" in organic and "2 years" in organic
    assert "Better Cotton" in f.say("better cotton").messages[0].text  # certificate name finds the crop topic
    assert "Aseel" in f.say("aseel").messages[0].text


def test_free_text_routes_to_ask_anything_during_a_step(db):
    f = Farmer(db)
    f.onboard()
    f.say(option_id="menu:weather")
    r = f.say("how do I control pink bollworm")
    assert "pink bollworm" in r.messages[0].text.lower()
    assert r.state == "WEATHER_DISTRICT"  # active step is preserved


def test_question_mentioning_a_crop_is_not_taken_as_a_selection(db):
    f = Farmer(db)
    f.onboard()
    f.say(option_id="menu:crops")
    f.say("cotton")
    r = f.say("How much urea for wheat?")
    assert "urea" in r.messages[0].text.lower()  # answered from the knowledge base
    assert r.state == "CROP_DISTRICT"
    assert "Sukkur" in f.say("sukkur weather").messages[0].text  # short replies still select


def test_ask_anything_fallback(db):
    f = Farmer(db)
    f.onboard()
    f.say(option_id="menu:ask")
    r = f.say("tell me about the stock market")
    assert "not currently available" in r.messages[0].text


def test_home_returns_to_menu_from_any_step(db):
    f = Farmer(db)
    f.onboard()
    f.say(option_id="menu:crops")
    r = f.say(option_id="nav:home")
    assert r.state == "MAIN_MENU"


def test_usage_recorded_only_with_consent(db):
    yes = Farmer(db, ref="consenting")
    yes.onboard(usage=True)
    yes.say("1")  # Weather
    yes.say("sukkur")
    recorded = usage_count(db)
    assert recorded > 0

    no = Farmer(db, ref="declining")
    no.onboard(usage=False)
    no.say("1")
    r = no.say("sukkur")
    assert "Sukkur" in r.messages[0].text  # still gets the answer
    assert usage_count(db) == recorded  # but nothing new recorded


def test_feedback_button_through_engine(db):
    f = Farmer(db, channel="whatsapp", ref="923001234567")
    f.onboard()
    f.say("1")
    answer = f.say("ghotki").messages[0]
    r = f.say(option_id=feedback_option_id(True, answer.service, answer.id))
    # Thanks and the main menu arrive in one message, so continuing costs nothing extra.
    assert len(r.messages) == 1 and "Thank you" in r.messages[0].text
    assert r.state == "MAIN_MENU" and r.messages[0].options[0].id == "menu:weather"
    fb = db.scalar(select(Feedback))
    assert fb.helpful is True and fb.service == "weather"


def test_phone_number_is_never_stored(db):
    f = Farmer(db, channel="whatsapp", ref="923001234567")
    f.onboard()
    from app.models import FarmerConsent

    farmer = db.scalar(select(FarmerConsent))
    assert "923001234567" not in farmer.external_ref_hash


def test_voice_note_gets_polite_reply(db):
    f = Farmer(db)
    f.onboard()
    r = f.say(kind=InboundKind.VOICE)
    assert "Voice notes are not supported" in r.messages[0].text


@pytest.mark.parametrize("channel", ["web", "whatsapp"])
def test_same_engine_for_every_channel(db, channel):
    f = Farmer(db, channel=channel, ref=f"{channel}-user")
    r = f.onboard()
    assert r.state == "MAIN_MENU"


def test_redelivered_webhook_is_not_answered_twice(db):
    from app.models import ProcessedMessage

    f = Farmer(db, channel="whatsapp", ref="923001234567")
    f.onboard()
    first = f.say(option_id="menu:weather", message_id="wamid.ABC")
    assert len(first.messages) == 1
    again = f.say(option_id="menu:weather", message_id="wamid.ABC")
    assert again.messages == []
    stored = db.scalar(select(ProcessedMessage))
    assert "ABC" not in stored.message_hash  # only a hash of the id is kept


def test_quick_double_tap_gets_one_reply(db):
    f = Farmer(db)
    f.onboard()
    assert len(f.say(option_id="menu:crops").messages) == 1
    assert f.say(option_id="menu:crops").messages == []  # same button again within seconds
    assert len(f.say(option_id="crop:wheat").messages) == 1


def test_typed_repeats_are_still_answered(db):
    f = Farmer(db)
    f.onboard()
    assert f.say("hi").messages and f.say("hi").messages


def test_outbound_messages_are_counted_per_channel(db):
    from app.models import OutboundMessageCount

    Farmer(db, channel="whatsapp", ref="923001234567").onboard()  # 4 bot messages
    Farmer(db, channel="web", ref="browser").onboard()
    counts = {row.channel: row.count for row in db.scalars(select(OutboundMessageCount))}
    assert counts == {"whatsapp": 4, "web": 4}
