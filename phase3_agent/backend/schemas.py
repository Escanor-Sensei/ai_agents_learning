"""
Schemas — schemas.py
Pydantic models for the blog generation API.

.NET analogy:
  BlogRequest  ≈  [FromBody] DTO on a POST action
  BlogResponse ≈  typed ActionResult<T> returned from the controller

Intentionally minimal — no sessions, no conversation history,
no tool calls. Blog generation is a stateless one-shot request.
"""

from pydantic import BaseModel, Field


class BlogRequest(BaseModel):
    topic: str = Field(..., min_length=3, description="The topic to generate a blog post about")


class BlogResponse(BaseModel):
    topic: str
    blog_post: str
    outline: str
    research_notes: str
    supervisor_feedback: str
    retry_count: int = Field(description="How many times the supervisor re-routed (0 = passed first try)")
