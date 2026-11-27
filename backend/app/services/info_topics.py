"""Shared loader for static, step-by-step information topics (credit, certifications)."""
from dataclasses import dataclass

from app.i18n import LocalizedText
from app.services.data_loader import load_json


@dataclass(frozen=True)
class InfoSection:
    heading: LocalizedText
    items: list[LocalizedText]


@dataclass(frozen=True)
class InfoTopic:
    id: str
    label: LocalizedText
    title: LocalizedText
    summary: LocalizedText
    sections: list[InfoSection]
    # Other words a farmer may type for this topic ("better cotton" -> cotton). Matching only.
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class InfoIntro:
    """General guidance shown above a topic menu (for example 'Certification: start here')."""
    summary: LocalizedText
    sections: list[InfoSection]


def _sections(raw: list[dict]) -> list[InfoSection]:
    return [InfoSection(s["heading"], s["items"]) for s in raw]


class StaticInfoService:
    filename: str
    collection_key: str

    def __init__(self) -> None:
        data = load_json(self.filename)
        raw = data[self.collection_key]
        intro = data.get("intro")
        self._intro = InfoIntro(intro["summary"], _sections(intro.get("sections", []))) if intro else None
        self._topics = [
            InfoTopic(
                id=t["id"],
                label=t["label"],
                title=t["title"],
                summary=t["summary"],
                sections=_sections(t["sections"]),
                aliases=tuple(t.get("aliases", ())),
            )
            for t in raw
        ]

    def intro(self) -> InfoIntro | None:
        return self._intro

    def topics(self) -> list[InfoTopic]:
        return list(self._topics)

    def get(self, topic_id: str) -> InfoTopic | None:
        return next((t for t in self._topics if t.id == topic_id), None)
