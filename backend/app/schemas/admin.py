from typing import Any

from pydantic import BaseModel


class AdminLoginRequest(BaseModel):
    password: str


class AdminLoginResponse(BaseModel):
    token: str
    expires_at: int


class ContentPayload(BaseModel):
    content: Any
