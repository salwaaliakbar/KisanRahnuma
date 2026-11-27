"""The shared, channel-independent conversation engine.

    InboundMessage  ->  ConversationService.handle()  ->  ConversationResult

The web simulator calls this today; a WhatsApp webhook adapter will call exactly the
same method later. Nothing in here knows about HTTP, React or WhatsApp payloads.

Cost rules (every outbound WhatsApp message is billed; inbound ones are free):
  - each turn returns at most ONE message, which already carries the next step's buttons
  - a redelivered webhook (same message_id) or a quick double tap gets no reply at all
  - the farmer's district is remembered, so weather/crop rates skip the district question
  - outbound messages are counted per channel and month (OutboundCountRepository)

Routing order for every message:
  0. Duplicate delivery / double tap      -> no reply
  1. Feedback button (fb:...)            -> record it, reply with the main menu
  2. Voice note                           -> "not supported yet" reply
  3. Language button / language name      -> switch language (works at any step)
  4. Onboarding not finished              -> language, then district, then consent
  5. Greeting / "home" / Home button      -> main menu
     "language" / "zaban" / "boli"        -> language picker
  6. Handler for the current state        -> e.g. district selection
  7. Anything else with text              -> Ask Anything (state is kept)
"""
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.domain.messages import (
    ConversationResult,
    InboundKind,
    InboundMessage,
    Option,
    OutboundMessage,
    parse_feedback_option_id,
)
from app.domain.states import ConversationState as S
from app.domain.states import Service
from app.i18n import CATALOGUES, SUPPORTED_LANGUAGES, LocalizedText, all_variants, pick, t
from app.models import ConversationSession, FarmerConsent
from app.models.common import as_utc, utcnow
from app.repositories.message_repository import OutboundCountRepository, ProcessedMessageRepository
from app.repositories.session_repository import SessionRepository
from app.services import presenters as p
from app.services.certification_service import CertificationService
from app.services.consent_service import ConsentService, hash_external_ref
from app.services.credit_service import CreditService
from app.services.crop_service import CropService
from app.services.feedback_service import FeedbackService
from app.services.knowledge_service import KnowledgeService
from app.services.text_utils import normalize, tokens
from app.services.usage_service import UsageService
from app.services.weather_service import WeatherService



def _words(*groups: list[str]) -> frozenset[str]:
    """Normalized command words, so they compare equal to normalized farmer text."""
    return frozenset(normalize(word) for group in groups for word in group)


def _catalogue_words(key: str) -> list[str]:
    return [catalogue[key] for catalogue in CATALOGUES.values() if key in catalogue]


GLOBAL_COMMANDS = _words(
    ["hi", "hello", "hey", "salam", "assalam o alaikum", "assalamualaikum", "home", "menu", "main menu", "start"],
    ["سلام", "السلام علیکم", "اسلام علیکم", "السلام عليڪم", "مینو", "مینیو", "مينيو"],
    _catalogue_words("home"),
)
YES_WORDS = _words(
    ["yes", "y", "ok", "okay", "sure", "yeah", "yep", "haan", "han", "ji", "allow"],
    ["ہاں", "جی", "جی ہاں", "ٹھیک", "ها", "جي", "هائو", "ٺيڪ"],
    _catalogue_words("yes"),
)
NO_WORDS = _words(
    ["no", "n", "nope", "nahi", "nahin", "dont", "don t"],
    ["نہیں", "نہ", "جی نہیں", "نه", "ناهي", "نه جي"],
    _catalogue_words("no"),
)
# Typing a language's name switches to it at any step.
LANGUAGE_WORDS: dict[str, str] = {
    normalize(word): code
    for code, words in {
        "en": ["english", "angrezi", "انگریزی", "انگريزي"],
        "ur": ["urdu", "اردو"],
        "sd": ["sindhi", "سندھی", "سنڌي"],
    }.items()
    for word in words
}
# Typing one of these opens the language picker.
LANGUAGE_MENU_WORDS = _words(["language", "languages", "zaban", "zuban", "boli", "زبان", "ٻولي"])
MAX_SHORT_REPLY_WORDS = 2


@dataclass
class Turn:
    """Everything a handler needs for one incoming message."""

    farmer: FarmerConsent
    session: ConversationSession
    message: InboundMessage

    @property
    def lang(self) -> str:
        return self.farmer.language

    @property
    def text(self) -> str:
        return normalize(self.message.text)

    def go(self, state: S, **context: object) -> None:
        self.session.state = state.value
        self.session.context = dict(context)


Handler = Callable[[Turn], list[OutboundMessage] | None]


def localized_option(option_id: str, label: LocalizedText, lang: str) -> Option:
    """An option labelled in the farmer's language that also matches its other translations."""
    return Option(option_id, pick(label, lang), aliases=tuple(all_variants(label)))


def match_option(message: InboundMessage, options: list[Option]) -> Option | None:
    """Resolve a tapped button or typed reply ("2", "sukkur", "سکھر", "benazir") to one of the options."""
    if message.option_id:
        found = next((o for o in options if o.id == message.option_id), None)
        if found:
            return found
    text = normalize(message.text)
    if not text:
        return None
    if text.isdigit() and 1 <= int(text) <= len(options):
        return options[int(text) - 1]
    text_tokens = set(tokens(text, drop_stopwords=True))
    # Only short replies may pick an option by containing its name ("sukkur weather");
    # longer sentences are treated as questions for Ask Anything.
    is_short_reply = len(text_tokens) <= MAX_SHORT_REPLY_WORDS
    for option in options:
        key = option.id.split(":")[-1]
        if text == key:
            return option
        for name in (option.label, *option.aliases):
            if text == normalize(name):
                return option
            if text_tokens and text_tokens <= set(tokens(name, drop_stopwords=True)):  # "benazir" -> "Benazir Hari Card"
                return option
        if is_short_reply and tokens(key)[0] in text_tokens:  # "weather in sukkur" -> district:sukkur
            return option
    return None


def match_yes_no(message: InboundMessage) -> bool | None:
    if message.option_id:
        if message.option_id.endswith(":yes"):
            return True
        if message.option_id.endswith(":no"):
            return False
    text = normalize(message.text)
    if text in YES_WORDS:
        return True
    if text in NO_WORDS:
        return False
    return None


def match_language(message: InboundMessage) -> str | None:
    """A tapped language button (lang:ur) or a typed language name ("urdu", "سنڌي")."""
    if message.option_id and message.option_id.startswith(f"{p.LANGUAGE_OPTION_PREFIX}:"):
        code = message.option_id.split(":", 1)[1]
        return code if code in SUPPORTED_LANGUAGES else None
    return LANGUAGE_WORDS.get(normalize(message.text))


class ConversationService:
    def __init__(
        self,
        db: Session,
        settings: Settings | None = None,
        weather: WeatherService | None = None,
        crops: CropService | None = None,
        credit: CreditService | None = None,
        certifications: CertificationService | None = None,
        knowledge: KnowledgeService | None = None,
    ) -> None:
        self.db = db
        self.settings = settings or get_settings()
        self.consents = ConsentService(db, self.settings)
        self.usage = UsageService(db)
        self.feedback = FeedbackService(db)
        self.sessions = SessionRepository(db)
        self.processed = ProcessedMessageRepository(db)
        self.outbound_counts = OutboundCountRepository(db)
        self.weather = weather or WeatherService()
        self.crops = crops or CropService()
        self.credit = credit or CreditService()
        self.certifications = certifications or CertificationService()
        self.knowledge = knowledge or KnowledgeService()

        self._handlers: dict[S, Handler] = {
            S.CHOOSE_LANGUAGE: self._on_choose_language,
            S.CONSENT: self._on_consent,
            S.MAIN_MENU: self._on_main_menu,
            S.CHOOSE_DISTRICT: self._on_choose_district,
            S.WEATHER_DISTRICT: self._on_weather_district,
            S.CROP_SELECT: self._on_crop_select,
            S.CROP_DISTRICT: self._on_crop_district,
            S.CREDIT_MENU: self._on_credit_menu,
            S.CERT_MENU: self._on_cert_menu,
            S.ASK_ANYTHING: self._on_ask_anything,
        }

    # ------------------------------------------------------------------ entry point
    def handle(self, message: InboundMessage) -> ConversationResult:
        farmer = self.consents.get_or_create(message.channel, message.external_ref)
        session = self._active_session(farmer, message.channel)
        turn = Turn(farmer=farmer, session=session, message=message)

        if self._is_redelivery(message) or self._is_repeat_tap(turn):
            replies: list[OutboundMessage] = []  # already answered: replying again would cost a message
        else:
            replies = self._dispatch(turn)

        now = utcnow()
        session.last_activity_at = now
        session.last_option_id = message.option_id
        session.last_option_at = now if message.option_id else None
        if replies:
            self.outbound_counts.add(message.channel, now.strftime("%Y-%m"), len(replies))
        self.db.commit()
        return ConversationResult(
            farmer_id=farmer.farmer_id,
            session_id=session.id,
            state=session.state,
            messages=replies,
            language=farmer.language,
        )

    def _active_session(self, farmer: FarmerConsent, channel: str) -> ConversationSession:
        session = self.sessions.get_active(farmer.farmer_id)
        timeout = timedelta(minutes=self.settings.session_timeout_minutes)
        if session and utcnow() - as_utc(session.last_activity_at) > timeout:
            session.is_active = False
            session = None
        return session or self.sessions.create(farmer.farmer_id, channel, S.MAIN_MENU.value)

    def _is_redelivery(self, message: InboundMessage) -> bool:
        """True when this channel message id was already handled (e.g. a WhatsApp webhook retry)."""
        if not message.message_id:
            return False
        self.processed.prune(utcnow() - timedelta(days=self.settings.processed_message_retention_days))
        # Hashed: WhatsApp message ids encode the sender's phone number.
        message_hash = hash_external_ref(message.channel, message.message_id, self.settings.identity_hash_secret)
        return not self.processed.claim(message.channel, message_hash)

    def _is_repeat_tap(self, turn: Turn) -> bool:
        """The same button tapped again within a few seconds (slow network, impatient finger)."""
        session, option_id = turn.session, turn.message.option_id
        if not option_id or session.last_option_id != option_id or session.last_option_at is None:
            return False
        return utcnow() - as_utc(session.last_option_at) < timedelta(seconds=self.settings.repeat_tap_seconds)

    def _dispatch(self, turn: Turn) -> list[OutboundMessage]:
        msg = turn.message

        if msg.option_id and (fb := parse_feedback_option_id(msg.option_id)):
            helpful, service, response_id = fb
            self.feedback.record(turn.farmer, response_id, service, helpful, turn.session.id)
            # "Thanks" and the main menu in ONE message: the farmer's next step costs nothing extra.
            return self._show_main_menu(turn, intro=t("feedback_thanks", turn.lang))

        if msg.kind == InboundKind.VOICE:
            return [OutboundMessage(t("voice_unsupported", turn.lang), options=[p.home_option(turn.lang)])]

        if (lang := match_language(msg)) is not None:
            return self._set_language(turn, lang)

        state = S(turn.session.state)
        if not turn.farmer.consent_complete:
            if state in (S.CHOOSE_LANGUAGE, S.CHOOSE_DISTRICT, S.CONSENT):
                return self._handlers[state](turn) or []
            return self._start_onboarding(turn)

        if turn.text in GLOBAL_COMMANDS or msg.option_id == p.HOME_OPTION_ID:
            return self._show_main_menu(turn)
        if turn.text in LANGUAGE_MENU_WORDS:
            return self._show_language_picker(turn)

        replies = self._handlers[state](turn)
        if replies is not None:
            return replies

        if turn.text:
            return [self._answer_question(turn)]
        return [OutboundMessage(t("not_understood", turn.lang), options=[p.home_option(turn.lang)])]

    # ------------------------------------------------------------------ language
    def _show_language_picker(self, turn: Turn) -> list[OutboundMessage]:
        turn.go(S.CHOOSE_LANGUAGE)
        return [p.language_picker(turn.lang, with_home=turn.farmer.consent_complete)]

    def _on_choose_language(self, turn: Turn) -> list[OutboundMessage] | None:
        choice = match_option(turn.message, p.language_options())  # typed "1", "2", "3"
        if choice is not None:
            return self._set_language(turn, choice.id.split(":", 1)[1])
        if not turn.farmer.consent_complete:
            return [p.language_picker(turn.lang, with_home=False)]  # onboarding: ask again
        return None  # after onboarding: treat the text as a question

    def _set_language(self, turn: Turn, lang: str) -> list[OutboundMessage]:
        turn.farmer.language = lang
        self.usage.record(turn.farmer, turn.session.id, Service.MENU, "language_changed", {"language": lang})
        if not turn.farmer.consent_complete:
            return self._continue_onboarding(turn)  # continue onboarding in the new language
        return self._show_main_menu(turn, intro=t("language_changed", lang))

    # ------------------------------------------------------------------ onboarding & consent
    def _start_onboarding(self, turn: Turn) -> list[OutboundMessage]:
        """A new farmer first picks a language, so the next questions are readable.

        Onboarding is 4 messages: language picker, district (with the welcome), consent
        question, main menu. The district asked here is never asked again by weather or
        crop rates.
        """
        if turn.farmer.usage_consent is None:
            return self._show_language_picker(turn)
        return self._continue_onboarding(turn)

    def _continue_onboarding(self, turn: Turn) -> list[OutboundMessage]:
        if turn.farmer.district is None:
            return self._prompt_district(turn, onboarding=True)
        return self._start_consent(turn)

    def _start_consent(self, turn: Turn) -> list[OutboundMessage]:
        turn.go(S.CONSENT)
        return [p.consent_question(turn.lang)]

    def _on_consent(self, turn: Turn) -> list[OutboundMessage]:
        """Both permissions in one answer: a button, its number, or a typed yes (both) / no (neither)."""
        # Yes/no first: a typed "no" would otherwise match the "Only 1 (no updates)" label.
        if (answer := match_yes_no(turn.message)) is not None:
            usage = weekly = answer
        elif (choice := match_option(turn.message, p.consent_options(turn.lang))) is not None:
            usage, weekly = p.CONSENT_CHOICES[choice.id]
        else:
            return [p.consent_question(turn.lang, intro=t("consent_reask", turn.lang))]
        self.consents.set_usage_consent(turn.farmer, usage)
        self.consents.set_weekly_updates(turn.farmer, weekly)
        return self._show_main_menu(turn, intro=t("consent_done", turn.lang))

    # ------------------------------------------------------------------ main menu
    def _show_main_menu(self, turn: Turn, intro: str | None = None) -> list[OutboundMessage]:
        turn.go(S.MAIN_MENU)
        self.usage.record(turn.farmer, turn.session.id, Service.MENU, "main_menu_viewed")
        return [p.main_menu(turn.lang, intro)]

    def _on_main_menu(self, turn: Turn) -> list[OutboundMessage] | None:
        choice = match_option(turn.message, p.main_menu_options(turn.lang))
        if choice is None:
            return None
        match choice.id:
            case "menu:weather":
                return self._prompt_weather_district(turn)
            case "menu:crops":
                return self._prompt_crop(turn)
            case "menu:credit":
                turn.go(S.CREDIT_MENU)
                return [p.info_menu("credit_menu", self.credit.intro(), self._topic_options("credit", self.credit.topics(), turn.lang), turn.lang)]
            case "menu:certifications":
                turn.go(S.CERT_MENU)
                return [p.info_menu("cert_menu", self.certifications.intro(), self._topic_options("cert", self.certifications.topics(), turn.lang), turn.lang)]
            case "menu:ask":
                turn.go(S.ASK_ANYTHING)
                return [OutboundMessage(t("ask_prompt", turn.lang), options=[p.home_option(turn.lang)])]
            case "menu:district":
                return self._prompt_district(turn)
            case "menu:language":
                return self._show_language_picker(turn)
        return None

    # ------------------------------------------------------------------ farmer's district
    # The district is remembered on the farmer's record, so weather and crop rates answer
    # straight away instead of asking for it every time (one billed message fewer).
    @staticmethod
    def _district_options(districts, lang: str) -> list[Option]:
        return [localized_option(f"district:{d.id}", d.name, lang) for d in districts]

    def _all_districts(self) -> list:
        """Districts known to any service, in order and without duplicates."""
        seen: dict[str, object] = {}
        for d in [*self.weather.districts(), *self.crops.districts()]:
            seen.setdefault(d.id, d)
        return list(seen.values())

    @staticmethod
    def _saved_district(turn: Turn, districts):
        """The farmer's remembered district, if this service has data for it."""
        return next((d for d in districts if d.id == turn.farmer.district), None)

    def _prompt_district(self, turn: Turn, onboarding: bool = False) -> list[OutboundMessage]:
        turn.go(S.CHOOSE_DISTRICT)
        options = self._district_options(self._all_districts(), turn.lang)
        if onboarding:  # welcome + district, no Home button yet
            text = f"{t('welcome', turn.lang)}\n\n{t('district_pick', turn.lang)}"
            return [OutboundMessage(text, options=options)]
        return [p.choice_prompt(t("district_pick", turn.lang), options, turn.lang)]

    def _on_choose_district(self, turn: Turn) -> list[OutboundMessage] | None:
        onboarding = not turn.farmer.consent_complete
        choice = match_option(turn.message, self._district_options(self._all_districts(), turn.lang))
        if choice is None:
            # Onboarding: ask again. Afterwards: treat the text as a question.
            return self._prompt_district(turn, onboarding=True) if onboarding else None
        turn.farmer.district = choice.id.split(":", 1)[1]
        if onboarding:
            return self._start_consent(turn)
        return self._show_main_menu(turn, intro=t("district_saved", turn.lang, district=choice.label))

    # ------------------------------------------------------------------ weather
    def _prompt_weather_district(self, turn: Turn) -> list[OutboundMessage]:
        turn.go(S.WEATHER_DISTRICT)  # kept even when answering, so a typed district name still works
        saved = self._saved_district(turn, self.weather.districts())
        if saved and (answer := self._weather_answer(turn, saved.id)):
            return [answer]
        options = self._district_options(self.weather.districts(), turn.lang)
        return [p.choice_prompt(t("weather_pick_district", turn.lang), options, turn.lang)]

    def _on_weather_district(self, turn: Turn) -> list[OutboundMessage] | None:
        choice = match_option(turn.message, self._district_options(self.weather.districts(), turn.lang))
        if choice is None:
            return None
        district_id = choice.id.split(":", 1)[1]
        answer = self._weather_answer(turn, district_id)
        if answer is None:
            return None
        turn.farmer.district = district_id
        return [answer]  # state stays: farmer can type another district

    def _weather_answer(self, turn: Turn, district_id: str) -> OutboundMessage | None:
        report = self.weather.get_report(district_id)
        if report is None:
            if any(d.id == district_id for d in self.weather.districts()):
                # Known district but no forecast (e.g. Open-Meteo unreachable): say so, don't ask again.
                return OutboundMessage(t("weather_unavailable", turn.lang), options=[p.home_option(turn.lang)])
            return None
        self.usage.record(turn.farmer, turn.session.id, Service.WEATHER, "forecast_viewed", {"district": district_id})
        return p.weather_answer(report, turn.lang)

    # ------------------------------------------------------------------ crop rates
    def _crop_options(self, lang: str) -> list[Option]:
        return [localized_option(f"crop:{c.id}", c.name, lang) for c in self.crops.crops()]

    def _prompt_crop(self, turn: Turn) -> list[OutboundMessage]:
        turn.go(S.CROP_SELECT)
        saved = self._saved_district(turn, self.crops.districts())
        if saved:
            text = t("crop_pick_crop_in", turn.lang, district=pick(saved.name, turn.lang))
        else:
            text = t("crop_pick_crop", turn.lang)
        return [p.choice_prompt(text, self._crop_options(turn.lang), turn.lang)]

    def _select_crop(self, turn: Turn, crop_id: str) -> list[OutboundMessage]:
        """Answer at once for the remembered district, otherwise ask for the district first."""
        turn.go(S.CROP_DISTRICT, crop=crop_id)
        saved = self._saved_district(turn, self.crops.districts())
        if saved:
            return [self._crop_answer(turn, crop_id, saved.id, pick(saved.name, turn.lang))]
        crop = self.crops.get_crop(crop_id)
        text = t("crop_pick_district", turn.lang, crop=pick(crop.name, turn.lang) if crop else crop_id)
        return [p.choice_prompt(text, self._district_options(self.crops.districts(), turn.lang), turn.lang)]

    def _on_crop_select(self, turn: Turn) -> list[OutboundMessage] | None:
        choice = match_option(turn.message, self._crop_options(turn.lang))
        if choice is None:
            return None
        return self._select_crop(turn, choice.id.split(":", 1)[1])

    def _on_crop_district(self, turn: Turn) -> list[OutboundMessage] | None:
        crop_id = turn.session.context.get("crop")
        district = match_option(turn.message, self._district_options(self.crops.districts(), turn.lang))
        if district is None or not crop_id:
            # The farmer may have typed a different crop name instead.
            other_crop = match_option(turn.message, self._crop_options(turn.lang))
            return self._select_crop(turn, other_crop.id.split(":", 1)[1]) if other_crop else None
        district_id = district.id.split(":", 1)[1]
        turn.farmer.district = district_id
        return [self._crop_answer(turn, crop_id, district_id, district.label)]  # state stays

    def _crop_answer(self, turn: Turn, crop_id: str, district_id: str, district_label: str) -> OutboundMessage:
        report = self.crops.get_report(crop_id, district_id)
        if report is None:
            crop = self.crops.get_crop(crop_id)
            text = t("crop_unavailable", turn.lang, crop=pick(crop.name, turn.lang) if crop else crop_id, district=district_label)
            return p.answer(text, Service.CROP_RATES, turn.lang)
        self.usage.record(
            turn.farmer, turn.session.id, Service.CROP_RATES, "rate_viewed", {"crop": crop_id, "district": district_id}
        )
        return p.crop_answer(report, turn.lang)

    # ------------------------------------------------------------------ credit & certifications
    @staticmethod
    def _topic_options(prefix: str, topics, lang: str) -> list[Option]:
        options = [localized_option(f"{prefix}:{topic.id}", topic.label, lang) for topic in topics]
        return [replace(o, aliases=(*o.aliases, *topic.aliases)) for o, topic in zip(options, topics)]

    def _on_credit_menu(self, turn: Turn) -> list[OutboundMessage] | None:
        return self._on_info_menu(turn, "credit", self.credit, Service.CREDIT)

    def _on_cert_menu(self, turn: Turn) -> list[OutboundMessage] | None:
        return self._on_info_menu(turn, "cert", self.certifications, Service.CERTIFICATIONS)

    def _on_info_menu(self, turn: Turn, prefix: str, service, service_name: Service) -> list[OutboundMessage] | None:
        choice = match_option(turn.message, self._topic_options(prefix, service.topics(), turn.lang))
        if choice is None:
            return None
        topic = service.get(choice.id.split(":", 1)[1])
        self.usage.record(turn.farmer, turn.session.id, service_name, "info_viewed", {"topic": topic.id})
        return [p.info_answer(topic, service_name, turn.lang)]

    # ------------------------------------------------------------------ ask anything
    def _on_ask_anything(self, turn: Turn) -> list[OutboundMessage] | None:
        return [self._answer_question(turn)] if turn.text else None

    def _answer_question(self, turn: Turn) -> OutboundMessage:
        result = self.knowledge.search(turn.message.text or "")
        # Only the matched topic id is recorded, never the farmer's question text.
        if result:
            self.usage.record(turn.farmer, turn.session.id, Service.ASK_ANYTHING, "question_answered", {"topic": result.topic_id})
        else:
            self.usage.record(turn.farmer, turn.session.id, Service.ASK_ANYTHING, "question_unanswered")
        return p.knowledge_answer(result, turn.lang)
