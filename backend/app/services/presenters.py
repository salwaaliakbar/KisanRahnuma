"""Turns feature-service results into channel-neutral OutboundMessages.

All wording comes from the i18n catalogue (and localized data values via `pick`), so
switching language does not touch the conversation logic or the feature services.
"""
from datetime import date

from app.domain.messages import Option, OutboundMessage
from app.domain.states import Service
from app.i18n import LANGUAGE_NAMES, language_prompt, pick, t
from app.services.crop_service import CropRateReport
from app.services.info_topics import InfoIntro, InfoSection, InfoTopic
from app.services.knowledge_service import KnowledgeAnswer
from app.services.weather_service import WeatherReport

HOME_OPTION_ID = "nav:home"
LANGUAGE_OPTION_PREFIX = "lang"
MAIN_MENU_ITEMS = [
    ("menu:weather", "menu_weather"),
    ("menu:crops", "menu_crop_rates"),
    ("menu:credit", "menu_credit"),
    ("menu:certifications", "menu_certifications"),
    ("menu:ask", "menu_ask"),
    ("menu:district", "menu_district"),
    ("menu:language", "menu_language"),
]
CONSENT_OPTION_PREFIX = "consent"
# Both permissions in one question (one message instead of two):
#   option id -> (usage_consent, weekly_updates)
CONSENT_CHOICES: dict[str, tuple[bool, bool]] = {
    f"{CONSENT_OPTION_PREFIX}:both": (True, True),
    f"{CONSENT_OPTION_PREFIX}:usage": (True, False),
    f"{CONSENT_OPTION_PREFIX}:none": (False, False),
}


def money(value: float) -> str:
    return f"{value:,.0f}"


def home_option(lang: str) -> Option:
    return Option(HOME_OPTION_ID, t("home", lang))


def yes_no_options(prefix: str, lang: str) -> list[Option]:
    return [Option(f"{prefix}:yes", t("yes", lang)), Option(f"{prefix}:no", t("no", lang))]


def consent_options(lang: str) -> list[Option]:
    keys = ("consent_both", "consent_usage_only", "consent_none")
    return [Option(option_id, t(key, lang)) for option_id, key in zip(CONSENT_CHOICES, keys, strict=True)]


def consent_question(lang: str, intro: str | None = None) -> OutboundMessage:
    text = t("consent_q", lang)
    return OutboundMessage(text=f"{intro}\n\n{text}" if intro else text, options=consent_options(lang))


def language_options() -> list[Option]:
    """One button per language, always labelled in that language's own script."""
    return [Option(f"{LANGUAGE_OPTION_PREFIX}:{code}", name) for code, name in LANGUAGE_NAMES.items()]


def language_picker(lang: str, with_home: bool) -> OutboundMessage:
    # Three buttons (+ Home after onboarding = 4 -> a WhatsApp list message).
    options = [*language_options(), home_option(lang)] if with_home else language_options()
    return OutboundMessage(text=language_prompt(), options=options)


def main_menu_options(lang: str) -> list[Option]:
    return [Option(option_id, t(key, lang)) for option_id, key in MAIN_MENU_ITEMS]


def main_menu(lang: str, intro: str | None = None) -> OutboundMessage:
    text = t("main_menu", lang)
    return OutboundMessage(text=f"{intro}\n\n{text}" if intro else text, options=main_menu_options(lang))


def choice_prompt(text: str, options: list[Option], lang: str) -> OutboundMessage:
    return OutboundMessage(text=text, options=[*options, home_option(lang)])


def answer(text: str, service: Service, lang: str) -> OutboundMessage:
    """An answer: carries helpful Yes/No buttons in the same message, plus Home."""
    return OutboundMessage(text=text, options=[home_option(lang)], feedback=True, service=service.value)


def _day_label(day: date, lang: str) -> str:
    delta = (day - date.today()).days
    if delta == 0:
        return t("today", lang)
    if delta == 1:
        return t("tomorrow", lang)
    return t(f"weekday_{day.weekday()}", lang)


def _short_date(day: date, lang: str) -> str:
    return f"{day.day:02d} {t(f'month_{day.month}', lang)}"


def weather_answer(report: WeatherReport, lang: str) -> OutboundMessage:
    lines = [t("weather_header", lang, district=pick(report.district.name, lang))]
    for d in report.days:
        lines.append(
            t(
                "weather_day",
                lang,
                day=_day_label(d.date, lang),
                date=_short_date(d.date, lang),
                condition=t(f"cond_{d.condition}", lang),
                temp_min=round(d.temp_min_c),
                temp_max=round(d.temp_max_c),
                rain=round(d.rain_mm),
                wind=round(d.wind_kmh),
            )
        )
    advice = " ".join(t(key, lang) for key in report.advice_keys)
    text = "\n".join(lines) + "\n\n" + t("weather_advice", lang, advice=advice) + "\n\n" + t("weather_followup", lang)
    return answer(text, Service.WEATHER, lang)


def crop_answer(r: CropRateReport, lang: str) -> OutboundMessage:
    unit = pick(r.crop.unit, lang)
    parts = [
        t("crop_rate", lang, crop=pick(r.crop.name, lang), district=pick(r.district.name, lang), rate=money(r.rate),
          unit=unit, source=pick(r.source, lang), date=r.date),
        t("crop_trend", lang, summer=money(r.trend.summer_avg), winter=money(r.trend.winter_avg),
          note=pick(r.trend.note, lang)),
        t("crop_expected", lang, season=pick(r.expected.season, lang), low=money(r.expected.low),
          high=money(r.expected.high), unit=unit, basis=pick(r.expected.basis, lang)),
        t("crop_followup", lang),
    ]
    return answer("\n\n".join(parts), Service.CROP_RATES, lang)


def _section_blocks(sections: list[InfoSection], lang: str) -> list[str]:
    blocks = []
    for section in sections:
        items = "\n".join(f"{i}. {pick(item, lang)}" for i, item in enumerate(section.items, start=1))
        blocks.append(f"*{pick(section.heading, lang)}*\n{items}")
    return blocks


def info_menu(menu_key: str, intro: InfoIntro | None, options: list[Option], lang: str) -> OutboundMessage:
    """A topic menu; the general guidance (intro), if any, goes in the same message as the list."""
    intro_text = "\n\n".join([pick(intro.summary, lang), *_section_blocks(intro.sections, lang)]) if intro else ""
    return choice_prompt(t(menu_key, lang, intro=intro_text), options, lang)


def info_answer(topic: InfoTopic, service: Service, lang: str) -> OutboundMessage:
    blocks = [f"*{pick(topic.title, lang)}*\n{pick(topic.summary, lang)}", *_section_blocks(topic.sections, lang)]
    if service == Service.CREDIT:
        blocks.append(t("credit_disclaimer", lang))
    elif service == Service.CERTIFICATIONS:
        blocks.append(t("cert_disclaimer", lang))
    blocks.append(t("info_followup", lang))
    return answer("\n\n".join(blocks), service, lang)


def knowledge_answer(result: KnowledgeAnswer | None, lang: str) -> OutboundMessage:
    if result is None:
        return answer(t("ask_fallback", lang), Service.ASK_ANYTHING, lang)
    text = f"{pick(result.answer, lang)}\n\n{t('ask_source', lang, source=pick(result.source, lang))}"
    return answer(text, Service.ASK_ANYTHING, lang)
