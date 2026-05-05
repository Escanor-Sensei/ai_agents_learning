"""
API Server — api.py
Exposes the ReAct agent as a REST API using FastAPI.

.NET analogy:
  FastAPI     ≈  ASP.NET Core Web API
  @app.post   ≈  [HttpPost] controller action
  CORS        ≈  app.UseCors() middleware
  AgentRunner ≈  scoped IAgentService injected into controller

One AgentRunner instance = one session (in-memory).
For multi-user support, sessions would be keyed by user ID.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from agent import AgentRunner

load_dotenv()

app = FastAPI(title="ReAct Agent API")

# Allow React dev server to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single shared session for now
# .NET analogy: singleton service — one conversation across all requests
runner = AgentRunner()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    session_id: str


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Accepts a user message, runs it through the ReAct agent, returns the reply.
    Memory is maintained automatically across calls via the shared runner.
    """
    reply = runner.run(request.message)
    return ChatResponse(reply=reply, session_id=runner.session_id)


@app.get("/health")
def health():
    return {"status": "ok", "model": runner.model, "tools": [t.name for t in runner.tools]}
