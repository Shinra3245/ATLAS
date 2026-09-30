"""Solicitud del chat de la guía. No transporta la clave de Claude."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1500)


class FactorBrief(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    status: str = Field(min_length=1, max_length=40)
    value: str = Field(default="", max_length=80)


class AssistantContext(BaseModel):
    route: str = Field(default="", max_length=80)
    phase: str = Field(default="", max_length=40)
    municipality: str = Field(default="", max_length=80)
    project: str = Field(default="", max_length=40)
    locality_a: str = Field(default="", max_length=120)
    locality_b: str = Field(default="", max_length=120)
    note: str = Field(default="", max_length=400)
    factors_a: list[FactorBrief] = Field(default_factory=list, max_length=16)
    factors_b: list[FactorBrief] = Field(default_factory=list, max_length=16)


class AssistantRequest(BaseModel):
    messages: list[ChatTurn] = Field(min_length=1, max_length=16)
    context: AssistantContext = Field(default_factory=AssistantContext)

    @model_validator(mode="after")
    def alternating_user_turns(self) -> AssistantRequest:
        if self.messages[0].role != "user" or self.messages[-1].role != "user":
            raise ValueError("la conversación debe empezar y terminar con el usuario")
        for previous, current in zip(self.messages, self.messages[1:]):
            if previous.role == current.role:
                raise ValueError("los mensajes deben alternar usuario y guía")
        return self


class AssistantReply(BaseModel):
    reply: str
