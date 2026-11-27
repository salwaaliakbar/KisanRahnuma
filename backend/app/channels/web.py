"""Web simulator channel: converts the React chat JSON to/from the engine's internal types.

A future channels/whatsapp.py will do the same job for WhatsApp webhook payloads.
"""
from app.domain.messages import ConversationResult, InboundKind, InboundMessage
from app.schemas.chat import ChatRequest, ChatResponse, MessageOut, OptionOut

CHANNEL = "web"


def to_inbound(request: ChatRequest) -> InboundMessage:
    if request.message_type == "voice":
        kind = InboundKind.VOICE
    elif request.option_id:
        kind = InboundKind.OPTION
    else:
        kind = InboundKind.TEXT
    return InboundMessage(
        channel=CHANNEL,
        external_ref=str(request.client_id),
        kind=kind,
        text=request.text,
        option_id=request.option_id,
    )


def to_response(result: ConversationResult) -> ChatResponse:
    return ChatResponse(
        farmer_id=result.farmer_id,
        session_id=result.session_id,
        state=result.state,
        language=result.language,
        messages=[
            MessageOut(
                id=m.id,
                text=m.text,
                options=[OptionOut(id=o.id, label=o.label) for o in m.options],
                feedback=m.feedback,
                service=m.service,
            )
            for m in result.messages
        ],
    )
