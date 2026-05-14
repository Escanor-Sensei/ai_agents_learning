from typing import Literal, Optional
from pydantic import BaseModel, Field


class ModeratorDecision(BaseModel):
    pro_summary: str = Field(description="2-3 sentence summary of Pro agent's overall argument")
    con_summary: str = Field(description="2-3 sentence summary of Con agent's overall argument")
    winner: Literal["Pro", "Con"] = Field(description="The winner of the debate")
    justification: str = Field(description="Clear justification for why this side won")


class DebateRequest(BaseModel):
    topic: str = Field(..., min_length=3, description="The topic to debate")


class RoundArguments(BaseModel):
    pro: str = ""
    con: str = ""


class DebateState(BaseModel):
    topic: str
    past_debates: list[dict] = []
    opening: RoundArguments = RoundArguments()
    rebuttal: RoundArguments = RoundArguments()
    closing: RoundArguments = RoundArguments()
    winner: str = ""
    summary: str = ""


class DebateResponse(BaseModel):
    topic: str
    winner: str
    summary: str
