import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langgraph")

from dotenv import load_dotenv
load_dotenv()

import asyncio
import json
from collections.abc import AsyncGenerator
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from agent import BlogRunner
from agent.core import get_graph
from agent.state import BlogState
from schemas import BlogRequest, BlogResponse

_executor = ThreadPoolExecutor(max_workers=2)
TIMEOUT_SECONDS = 300

app = FastAPI(
    title="Blog Generation Multi-Agent API",
    description="A supervised multi-agent pipeline that generates blog posts using Researcher, Analyst, Writer, and Supervisor agents.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Generation", "description": "Blog generation pipeline"},
        {"name": "Health", "description": "Server health checks"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

AGENT_LABELS = {
    "researcher": "🔍 Researcher is gathering information...",
    "analyst":    "📋 Analyst is building the outline...",
    "writer":     "✍️  Writer is writing the blog post...",
    "supervisor": "🧑‍⚖️ Supervisor is reviewing...",
}

STREAMING_NODES = {"researcher", "analyst", "writer"}


# ---------------------------------------------------------------------------
# Streaming
# ---------------------------------------------------------------------------

def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


async def _stream_generate(topic: str) -> AsyncGenerator:
    graph = get_graph()
    initial_state: BlogState = {
        "topic": topic,
        "research_notes": "",
        "outline": "",
        "blog_post": "",
        "supervisor_feedback": "",
        "next_node": "",
        "retry_count": 0,
    }
    current_node = None
    final_state = {}

    try:
        async for event in graph.astream_events(initial_state, version="v2"):
            kind = event["event"]
            name = event.get("name", "")

            if kind == "on_chain_start" and name in AGENT_LABELS:
                current_node = name
                yield _sse({"type": "label", "node": name, "text": AGENT_LABELS[name]})

            elif kind == "on_chat_model_stream" and current_node in STREAMING_NODES:
                token = event["data"]["chunk"].content
                if token:
                    yield _sse({"type": "token", "node": current_node, "token": token})

            elif kind == "on_chain_end" and name == "LangGraph":
                output = event["data"].get("output", {})
                if isinstance(output, dict):
                    final_state = output

        if final_state:
            yield _sse({
                "type": "result",
                "topic": final_state.get("topic", topic),
                "research_notes": final_state.get("research_notes", ""),
                "outline": final_state.get("outline", ""),
                "blog_post": final_state.get("blog_post", ""),
                "supervisor_feedback": final_state.get("supervisor_feedback", ""),
                "retry_count": final_state.get("retry_count", 0),
            })

    except Exception as e:
        yield _sse({"type": "error", "message": str(e)})

    yield "data: [DONE]\n\n"


@app.post("/generate/stream", tags=["Generation"], summary="Generate a blog post with streaming output")
async def generate_stream(request: BlogRequest):
    return StreamingResponse(
        _stream_generate(request.topic),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )


# ---------------------------------------------------------------------------
# Non-streaming (kept for /docs testing)
# ---------------------------------------------------------------------------

@app.post("/generate", response_model=BlogResponse, tags=["Generation"], summary="Generate a blog post")
async def generate(request: BlogRequest):
    try:
        loop = asyncio.get_event_loop()
        runner = BlogRunner()
        result = await asyncio.wait_for(
            loop.run_in_executor(_executor, runner.run, request.topic),
            timeout=TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Pipeline timed out.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return BlogResponse(
        topic=result.topic,
        blog_post=result.blog_post,
        outline=result.outline,
        research_notes=result.research_notes,
        supervisor_feedback=result.supervisor_feedback,
        retry_count=result.retry_count,
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
