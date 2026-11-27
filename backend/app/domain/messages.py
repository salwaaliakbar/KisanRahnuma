"""Channel-neutral message types used by the conversation engine.

The engine only ever receives an InboundMessage and returns a ConversationResult.
Each channel (web simulator now, WhatsApp later) converts its own payloads to and from
these types, so the business logic never depends on React or WhatsApp formats.

Constraints chosen to map cleanly onto WhatsApp interactive messages:
- up to 3 options  -> WhatsApp reply buttons (title <= 20 chars)
- 4..10 options    -> WhatsApp list message (row title <= 24 chars)
- feedback=True    -> the answer carries "Yes, helpful" / "Not helpful" buttons in the
                      SAME message, so it may have at most 1 extra option (Home).
- text of a message WITH options must stay <= MAX_INTERACTIVE_TEXT characters, otherwise
  the WhatsApp adapter has to send it as two messages (text, then the buttons).
Text may use WhatsApp-style *bold* markup.

Cost note: on WhatsApp every OUTBOUND message is billed (1,000 free per number per month)
and inbound messages are free. So each turn returns at most one message, and flows are
designed to need as few turns as possible.
"""
import uuid
from dataclasses import dataclass, field
from enum import StrEnum

MAX_OPTIONS = 10
MAX_OPTIONS_WITH_FEEDBACK = 1
MAX_OPTION_LABEL = 24
MAX_INTERACTIVE_TEXT = 1024  # WhatsApp body limit for button and list messages


class InboundKind(StrEnum):
    TEXT = "text"
    OPTION = "option"  # a tapped button / list row
    VOICE = "voice"  # voice note (speech-to-text not implemented yet)


@dataclass(frozen=True)
class InboundMessage:
    channel: str  # "web" | "whatsapp"
    external_ref: str  # browser client id, or WhatsApp wa_id later
    kind: InboundKind = InboundKind.TEXT
    text: str | None = None
    option_id: str | None = None
    # The channel's own id for this message (WhatsApp "wamid"). When set, a redelivered
    # webhook with the same id is ignored, so the farmer never gets (and we never pay for)
    # a duplicate reply.
    message_id: str | None = None


@dataclass(frozen=True)
class Option:
    id: str
    label: str
    # Other names the farmer may type for this option (e.g. the same district in another
    # language). Used only for matching; never sent to the channel.
    aliases: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if len(self.label) > MAX_OPTION_LABEL:
            raise ValueError(f"Option label too long for WhatsApp: {self.label!r}")


@dataclass
class OutboundMessage:
    text: str
    options: list[Option] = field(default_factory=list)
    feedback: bool = False  # answer carries helpful Yes/No buttons
    service: str | None = None  # service that produced the answer (for feedback/analytics)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def __post_init__(self) -> None:
        limit = MAX_OPTIONS_WITH_FEEDBACK if self.feedback else MAX_OPTIONS
        if len(self.options) > limit:
            raise ValueError(f"Too many options ({len(self.options)}) for one message")


@dataclass
class ConversationResult:
    farmer_id: uuid.UUID
    session_id: uuid.UUID
    state: str
    messages: list[OutboundMessage]
    language: str = "en"  # the farmer's current language, so channels can set text direction


# Feedback buttons travel as option ids so a WhatsApp button tap can carry them unchanged:
#   fb:<y|n>:<service>:<response_id>
FEEDBACK_PREFIX = "fb"


def feedback_option_id(helpful: bool, service: str, response_id: str) -> str:
    return f"{FEEDBACK_PREFIX}:{'y' if helpful else 'n'}:{service}:{response_id}"


def parse_feedback_option_id(option_id: str) -> tuple[bool, str, str] | None:
    parts = option_id.split(":")
    if len(parts) != 4 or parts[0] != FEEDBACK_PREFIX or parts[1] not in ("y", "n"):
        return None
    return parts[1] == "y", parts[2], parts[3]
