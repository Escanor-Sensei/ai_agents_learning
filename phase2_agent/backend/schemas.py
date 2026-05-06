"""
Schemas — schemas.py
Pydantic models for structured input/output across the agent stack.

.NET analogy:
  ChatRequest   ≈  [FromBody] DTO on a POST action
  AgentResponse ≈  typed ActionResult<T> returned from the controller
  ToolCall      ≈  a value object capturing what middleware/service was invoked
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    user_id: str = Field(..., description="Browser-generated UUID from localStorage")
    session_id: str | None = Field(None, description="Resume existing LangGraph session")
    conversation_id: str | None = Field(None, description="Resume existing conversation")


class ToolCall(BaseModel):
    name: str
    input: str
    output: str


class AgentResponse(BaseModel):
    reply: str
    session_id: str
    model: str
    tool_calls: list[ToolCall] = Field(default_factory=list)


class ChatResponse(AgentResponse):
    conversation_id: str


class ConversationOut(BaseModel):
    conversation_id: str
    session_id: str
    title: str
    created_at: str
    updated_at: str


class MessageOut(BaseModel):
    message_id: int
    role: str
    content: str
    tool_calls: list | None
    created_at: str
