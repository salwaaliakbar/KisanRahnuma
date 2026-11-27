from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.channels import web
from app.database.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    result = ConversationService(db).handle(web.to_inbound(request))
    return web.to_response(result)
