import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langgraph")

import asyncio
import json
import uuid
from collections.abc import AsyncGenerator
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from graph.debate_graph import build_graph, DebateGraphState
from schemas import DebateRequest, DebateResponse, DebateResumeRequest

_executor = ThreadPoolExecutor(max_workers=2)
TIMEOUT_SECONDS = 300

app = FastAPI(
    title="Debate Chatbot API",
    description="Real-time multi-agent debate chatbot with memory.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Debate", "description": "Debate pipeline"},
        {"name": "Health", "description": "Server health checks"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_graph = build_graph()

TURN_LABELS = {
    "pro_opening":   "🎤 Pro Agent is presenting opening arguments...",
    "con_opening":   "🎤 Con Agent is presenting opening arguments...",
    "moderator_route": "🧭 Moderator is deciding the next phase...",
    "pro_rebuttal":  "⚔️  Pro Agent is rebutting...",
    "con_rebuttal":  "⚔️  Con Agent is rebutting...",
    "pro_closing":   "🏁 Pro Agent is giving closing remarks...",
    "con_closing":   "🏁 Con Agent is giving closing remarks...",
    "moderator":     "⚖️  Moderator is evaluating...",
}

AGENT_NODES = {
    "pro_opening":  "Pro",
    "con_opening":  "Con",
    "pro_rebuttal": "Pro",
    "con_rebuttal": "Con",
    "pro_closing":  "Pro",
    "con_closing":  "Con",
}


# ---------------------------------------------------------------------------
# Streaming debate — token by token
# ---------------------------------------------------------------------------

async def _stream_graph(config: dict, input_or_command) -> AsyncGenerator:
    from langgraph.errors import GraphInterrupt
    current_node = None
    interrupted = False
    try:
        async for event in _graph.astream_events(input_or_command, config=config, version="v2"):
            kind = event["event"]
            name = event.get("name", "")

            if kind == "on_chain_start" and name in TURN_LABELS:
                current_node = name
                yield f"data: {json.dumps({'type': 'label', 'text': TURN_LABELS[name], 'node': name})}\n\n"

            elif kind == "on_chat_model_stream" and current_node in AGENT_NODES:
                token = event["data"]["chunk"].content
                if token:
                    yield f"data: {json.dumps({'type': 'token', 'side': AGENT_NODES[current_node], 'node': current_node, 'token': token})}\n\n"

            elif kind == "on_chain_end" and name == "moderator":
                output = event["data"].get("output", {})
                if isinstance(output, dict) and output.get("winner"):
                    yield f"data: {json.dumps({'type': 'result', 'winner': output['winner'], 'summary': output['summary']})}\n\n"

    except GraphInterrupt:
        interrupted = True
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    # Check graph state for interrupt after stream ends
    if not interrupted:
        state = _graph.get_state(config)
        if state.next and state.tasks:
            interrupted = True

    if interrupted:
        thread_id = config["configurable"]["thread_id"]
        print(f"[INTERRUPT] thread_id={thread_id}")
        yield f"data: {json.dumps({'type': 'interrupt', 'thread_id': thread_id})}\n\n"

    yield "data: [DONE]\n\n"


@app.post("/debate/stream", tags=["Debate"], summary="Run a debate with streaming output")
async def debate_stream(request: DebateRequest):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    initial_state: DebateGraphState = {
        "topic": request.topic,
        "past_debates": [],
        "pro_opening": "",
        "con_opening": "",
        "pro_rebuttal": "",
        "con_rebuttal": "",
        "pro_closing": "",
        "con_closing": "",
        "winner": "",
        "summary": "",
        "next_phase": "",
        "human_decision": "",
    }
    return StreamingResponse(
        _stream_graph(config, initial_state),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )


@app.post("/debate/resume", tags=["Debate"], summary="Resume a debate after human review")
async def debate_resume(request: DebateResumeRequest):
    from langgraph.types import Command
    config = {"configurable": {"thread_id": request.thread_id}}
    command = Command(resume=request.decision)
    return StreamingResponse(
        _stream_graph(config, command),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"], summary="Health check")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
