"""
Blog Runner — agent/runner.py

Responsible for invoking the graph and returning a typed result.

Mirrors phase2's runner.py pattern:
  phase2 → AgentRunner.run(user_input) returned AgentResponse
  phase3 → BlogRunner.run(topic)       returns BlogResult

Separation of concerns:
  core.py    → HOW the graph is built       (construction)
  runner.py  → HOW the graph is invoked     (execution)
  api.py     → HOW the user calls it        (HTTP layer)

.NET analogy:
  BlogRunner = a scoped service your controller calls
  run()      = the method that executes the pipeline and returns a DTO
"""

from dataclasses import dataclass
from agent.core import get_graph
from agent.state import BlogState


@dataclass
class BlogResult:
    """
    Typed result returned to the API layer.
    Exposes all state fields so the caller can see the full pipeline output,
    not just the final blog post.
    """
    topic: str
    research_notes: str
    outline: str
    blog_post: str
    supervisor_feedback: str
    retry_count: int


class BlogRunner:
    """
    Executes the blog generation graph for a given topic.

    Each call to run() is a fresh, stateless graph invocation —
    no session or memory needed since blog generation is a one-shot task.

    .NET analogy: A transient service — new instance per request,
    no shared state between calls.
    """

    def __init__(self):
        self._graph = get_graph()

    def run(self, topic: str) -> BlogResult:
        """
        Invokes the full multi-agent pipeline and returns a BlogResult.

        Initial state seeds all fields with empty defaults so every node
        has a safe value to read from on first run.

        Concept: graph.invoke() runs the entire graph synchronously —
        START → researcher → analyst → writer → supervisor → (re-route or END)
        — and returns the final accumulated state dict when it hits END.
        """
        initial_state: BlogState = {
            "topic": topic,
            "research_notes": "",
            "outline": "",
            "blog_post": "",
            "supervisor_feedback": "",
            "next_node": "",
            "retry_count": 0,
        }

        final_state: BlogState = self._graph.invoke(initial_state)

        return BlogResult(
            topic=final_state["topic"],
            research_notes=final_state["research_notes"],
            outline=final_state["outline"],
            blog_post=final_state["blog_post"],
            supervisor_feedback=final_state.get("supervisor_feedback", ""),
            retry_count=final_state.get("retry_count", 0),
        )
