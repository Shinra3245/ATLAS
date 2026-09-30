"""Chat de la guía triangular. No expone la clave de Claude."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.assistant import AssistantReply, AssistantRequest
from app.services.assistant import complete

router = APIRouter(tags=["assistant"])


@router.post("/assistant", response_model=AssistantReply)
def assistant(body: AssistantRequest) -> AssistantReply:
    return AssistantReply(reply=complete(body))
