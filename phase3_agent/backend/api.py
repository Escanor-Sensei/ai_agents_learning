"""
API Server — api.py
Exposes the multi-agent blog generation pipeline as a REST API.

.NET analogy:
  FastAPI       ≈  ASP.NET Core Web API
  @app.post     ≈  [HttpPost] controller action
  CORS          ≈  app.UseCors() middleware
  BlogRunner    ≈  scoped service injected into the controller

Intentionally simpler than phase2 — no sessions, no DB, no conversation history.
One endpoint: POST /generate → runs the full pipeline → returns the blog.
"""

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langgraph")

import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agent import BlogRunner
from schemas import BlogRequest, BlogResponse

_executor = ThreadPoolExecutor(max_workers=2)
TIMEOUT_SECONDS = 300  # 5 min max

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


# ---------------------------------------------------------------------------
# Blog Generation
# ---------------------------------------------------------------------------

@app.post("/generate", response_model=BlogResponse, tags=["Generation"], summary="Generate a blog post")
async def generate(request: BlogRequest):
    """
    Runs the supervised multi-agent pipeline:
      Supervisor → Researcher → Supervisor → Analyst → Supervisor → Writer → Supervisor → END

    The Supervisor coordinates every step. Agents never call each other directly.
    Returns the final blog post along with intermediate outputs
    (outline, research notes) and supervisor metadata (feedback, retry count).

    .NET analogy: A POST action that calls a service, awaits the result,
    and returns a typed ActionResult<BlogResponse>.
    """
    try:
        loop = asyncio.get_event_loop()
        runner = BlogRunner()
        result = await asyncio.wait_for(
            loop.run_in_executor(_executor, runner.run, request.topic),
            timeout=TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Pipeline timed out (>5 min). Try a smaller model or shorter topic.")
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
