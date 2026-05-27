from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

Denomination = Literal[
    "protestant", "catholic", "orthodox", "evangelical", "non_denominational"
]


class ChatRequest(BaseModel):
    session_id: UUID
    message: str = Field(..., min_length=1, max_length=2000)
    denomination: Denomination = "protestant"
    mode: Literal["text", "image"] = "text"


class VerseCitation(BaseModel):
    reference: str
    text: str
    verified: bool


class ChatResponse(BaseModel):
    session_id: UUID
    response: str
    citations: list[VerseCitation] = Field(default_factory=list)
    image_url: str | None = None
    safety_blocked: bool = False
    block_reason: str | None = None
    denomination_notes: str | None = None
    retrieval_score: float | None = None


class ImageRequest(BaseModel):
    session_id: UUID
    prompt: str = Field(..., min_length=3, max_length=500)
    denomination: Denomination = "protestant"
    style: str = Field(default="classical painting", max_length=80)


class ImageResponse(BaseModel):
    image_url: str | None
    revised_prompt: str
    safety_blocked: bool
    block_reason: str | None = None


class HistoryTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: str
    citations: list[VerseCitation] = Field(default_factory=list)


class HistoryResponse(BaseModel):
    session_id: UUID
    turns: list[HistoryTurn]
