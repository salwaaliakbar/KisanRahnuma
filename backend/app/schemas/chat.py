import uuid
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ChatRequest(BaseModel):
    client_id: uuid.UUID = Field(description="Random id generated and stored by the browser")
    text: str | None = Field(default=None, max_length=1000)
    option_id: str | None = Field(default=None, max_length=200)
    message_type: Literal["text", "voice"] = "text"

    @model_validator(mode="after")
    def require_content(self) -> "ChatRequest":
        if self.message_type == "text" and not (self.text and self.text.strip()) and not self.option_id:
            raise ValueError("Either text or option_id is required")
        return self


class OptionOut(BaseModel):
    id: str
    label: str


class MessageOut(BaseModel):
    id: str
    text: str
    options: list[OptionOut]
    feedback: bool
    service: str | None


class ChatResponse(BaseModel):
    farmer_id: uuid.UUID
    session_id: uuid.UUID
    state: str
    language: str = Field(description="Farmer's language: en, ur or sd")
    messages: list[MessageOut]
