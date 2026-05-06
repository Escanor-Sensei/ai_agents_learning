"""
API Server — api.py
Exposes the ReAct agent and conversation history as a REST API.

.NET analogy:
  FastAPI     ≈  ASP.NET Core Web API
  @app.post   ≈  [HttpPost] controller action
  CORS        ≈  app.UseCors() middleware
  AgentRunner ≈  scoped IAgentService injected into controller
"""

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langgraph")
warnings.filterwarnings("ignore", message=".*allowed_objects.*")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agent import AgentRunner
from schemas import ChatRequest, AgentResponse, ChatResponse, ConversationOut, MessageOut
import db.conversation_repo as repo

app = FastAPI(title="ReAct Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session registry: session_id -> AgentRunner
_sessions: dict[str, AgentRunner] = {}


def _get_runner(session_id: str | None) -> AgentRunner:
    if session_id and session_id in _sessions:
        return _sessions[session_id]
    runner = AgentRunner()
    _sessions[runner.session_id] = runner
    return runner


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@app.post("/users/ensure")
def ensure_user(payload: dict):
    user_id = payload.get("user_id", "").strip()
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    repo.ensure_user(user_id)
    return {"user_id": user_id}


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    runner = _get_runner(request.session_id)

    # Create conversation on first message, reuse on subsequent turns
    conversation_id = request.conversation_id or repo.create_conversation(
        user_id=request.user_id,
        session_id=runner.session_id,
        first_message=request.message,
    )

    # Load full history from DB for long-term memory
    # Only needed on a fresh runner (new session) — MemorySaver handles in-session turns
    is_new_session = request.session_id not in _sessions
    history = repo.get_messages(conversation_id) if is_new_session and request.conversation_id else None

    # Persist user message
    repo.save_message(conversation_id, role="user", content=request.message)

    # Run agent with history
    response = runner.run(request.message, history=history)

    # Persist assistant reply
    tool_calls_raw = [tc.model_dump() for tc in response.tool_calls]
    repo.save_message(
        conversation_id,
        role="assistant",
        content=response.reply,
        tool_calls=tool_calls_raw or None,
    )

    return ChatResponse(
        reply=response.reply,
        session_id=runner.session_id,
        conversation_id=conversation_id,
        model=response.model,
        tool_calls=response.tool_calls,
    )


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

@app.get("/conversations/{user_id}", response_model=list[ConversationOut])
def get_conversations(user_id: str):
    rows = repo.get_conversations(user_id)
    return [
        ConversationOut(
            conversation_id=r["conversation_id"],
            session_id=r["session_id"],
            title=r["title"],
            created_at=str(r["created_at"]),
            updated_at=str(r["updated_at"]),
        )
        for r in rows
    ]


@app.get("/conversations/{user_id}/{conversation_id}/messages", response_model=list[MessageOut])
def get_messages(user_id: str, conversation_id: str):
    # Verify conversation belongs to this user
    convs = repo.get_conversations(user_id)
    if not any(c["conversation_id"] == conversation_id for c in convs):
        raise HTTPException(status_code=404, detail="Conversation not found")

    rows = repo.get_messages(conversation_id)
    return [
        MessageOut(
            message_id=r["message_id"],
            role=r["role"],
            content=r["content"],
            tool_calls=r["tool_calls"],
            created_at=str(r["created_at"]),
        )
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    runner = _get_runner(None)
    return {"status": "ok", "model": runner.model, "tools": [t.name for t in runner.tools]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
