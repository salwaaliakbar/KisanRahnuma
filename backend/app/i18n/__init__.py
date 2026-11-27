"""String catalogues for bot wording, keyed by language.

Supported: English (en), Urdu (ur), Sindhi (sd). Data files (districts, crops, info
topics, knowledge base) carry their own translations as {"en": ..., "ur": ..., "sd": ...}
objects, resolved with `pick()`. Conversation logic never contains wording.
"""
from collections.abc import Mapping

from app.i18n.en import STRINGS as EN
from app.i18n.sd import STRINGS as SD
from app.i18n.ur import STRINGS as UR

CATALOGUES: dict[str, dict[str, str]] = {"en": EN, "ur": UR, "sd": SD}
DEFAULT_LANGUAGE = "en"

# Native names, shown on the language buttons regardless of the current language.
LANGUAGE_NAMES: dict[str, str] = {"en": "English", "ur": "اردو", "sd": "سنڌي"}
SUPPORTED_LANGUAGES = tuple(LANGUAGE_NAMES)
RTL_LANGUAGES = frozenset({"ur", "sd"})

# A localized value from a data file: either a plain string (same in every language)
# or a {"en": ..., "ur": ..., "sd": ...} mapping.
LocalizedText = str | Mapping[str, str]


def t(key: str, lang: str = DEFAULT_LANGUAGE, **kwargs: object) -> str:
    catalogue = CATALOGUES.get(lang, CATALOGUES[DEFAULT_LANGUAGE])
    template = catalogue.get(key) or CATALOGUES[DEFAULT_LANGUAGE][key]
    return template.format(**kwargs) if kwargs else template


def pick(value: LocalizedText, lang: str = DEFAULT_LANGUAGE) -> str:
    """Resolve a localized data value, falling back to English when a translation is missing."""
    if isinstance(value, str):
        return value
    return value.get(lang) or value.get(DEFAULT_LANGUAGE) or next(iter(value.values()), "")


def all_variants(value: LocalizedText) -> list[str]:
    """Every translation of a value (used to match typed text in any language)."""
    return [value] if isinstance(value, str) else list(value.values())


def language_prompt() -> str:
    """The language question, written in all three languages so anyone can read it."""
    return "\n".join(t("language_prompt_line", lang) for lang in SUPPORTED_LANGUAGES)
