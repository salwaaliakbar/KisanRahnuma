import uuid

from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    client_id: uuid.UUID
    response_id: str = Field(min_length=1, max_length=64)
    service: str = Field(min_length=1, max_length=40)
    helpful: bool


class FeedbackResponse(BaseModel):
    status: str = "recorded"
    linked_to_farmer: bool
