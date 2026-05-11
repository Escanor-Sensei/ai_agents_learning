"""
Supervisor + Graph — agent/supervisor.py

The Supervisor is the ONLY entry point and coordinator.
It runs first, decides which agent to call next, and runs again after
every agent completes — forming a hub-and-spoke topology:

  START → supervisor → researcher → supervisor
                    ↘ analyst    ↗
                    ↘ writer     ↗
                    ↘ END (when FINISH)

This means the supervisor controls the flow at every step, not the graph topology.
Agents never call each other — they only report back to the supervisor.

Routing logic:
  - No research yet       → dispatch researcher
  - Research done, no outline → dispatch analyst
  - Outline done, no blog → dispatch writer
  - Blog exists           → review quality, FINISH or re-dispatch with feedback

Retry guard: retry_count prevents infinite loops (max 2 quality re-routes).
"""

from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

from agent.state import BlogState
from agent.llm import get_llm
from agent.researcher import researcher_node
from agent.analyst import analyst_node
from agent.writer import writer_node

_llm = get_llm()

MAX_RETRIES = 2


class SupervisorDecision(BaseModel):
    feedback: str = Field(description="Specific, actionable feedback for the target agent. Empty if dispatching for the first time or FINISH.")
    next_node: Literal["researcher", "analyst", "writer", "FINISH"] = Field(
        description=(
            "researcher → gather information on the topic. "
            "analyst → extract insights and build an outline from research. "
            "writer → write the blog post from the outline. "
            "FINISH → blog is complete and meets quality bar."
        )
    )


_routing_llm = _llm.with_structured_output(SupervisorDecision)

_SYSTEM = """You are a senior editorial supervisor coordinating a blog generation pipeline.

You will receive the current state of the pipeline: topic, research notes, outline, and blog post.
Your job is to decide what to do next.

Dispatching rules (follow in order):
1. If research_notes is empty → dispatch researcher
2. If outline is empty        → dispatch analyst
3. If blog_post is empty      → dispatch writer
4. If blog_post exists        → review it:
   - FINISH     → blog is clear, well-structured, ~500 words, covers the topic well
   - writer     → blog has issues (too short, unclear, poor tone, missing points)
   - analyst    → outline is missing key sections or poorly organized
   - researcher → research is too shallow, missing key concepts, or off-topic

Always route to the EARLIEST agent that can fix the root problem.
Provide specific, actionable feedback when re-dispatching."""


def supervisor_node(state: BlogState) -> dict:
    """
    The central coordinator. Runs at every step to decide which agent goes next.

    On first run: research_notes/outline/blog_post are all empty, so the
    supervisor dispatches researcher immediately without an LLM call (fast path).

    After each agent completes: supervisor reviews the updated state and
    dispatches the next agent or finishes.

    Circuit breaker: if retry_count >= MAX_RETRIES, forces FINISH.
    """
    retry_count = state.get("retry_count", 0)

    # Fast-path dispatch: no LLM call needed when pipeline hasn't started
    if not state.get("research_notes"):
        return {"next_node": "researcher", "supervisor_feedback": ""}
    if not state.get("outline"):
        return {"next_node": "analyst", "supervisor_feedback": ""}
    if not state.get("blog_post"):
        return {"next_node": "writer", "supervisor_feedback": ""}

    # Circuit breaker: blog exists but we've hit the retry limit
    if retry_count >= MAX_RETRIES:
        return {"next_node": "FINISH", "supervisor_feedback": ""}

    # Quality review: blog exists — LLM decides if it's good or needs rework
    decision: SupervisorDecision = _routing_llm.invoke([
        SystemMessage(content=_SYSTEM),
        HumanMessage(content=(
            f"Topic: {state['topic']}\n\n"
            f"Research Notes:\n{state['research_notes']}\n\n"
            f"Outline:\n{state['outline']}\n\n"
            f"Blog Post:\n{state['blog_post']}\n\n"
            "What should happen next?"
        )),
    ])

    new_retry_count = retry_count + 1 if decision.next_node != "FINISH" else retry_count

    return {
        "next_node": decision.next_node,
        "supervisor_feedback": decision.feedback,
        "retry_count": new_retry_count,
    }


def route_after_supervisor(state: BlogState) -> Literal["researcher", "analyst", "writer", "__end__"]:
    """
    Routing function called by LangGraph after every supervisor run.
    Maps next_node → graph node name (or END).
    """
    next_node = state.get("next_node", "FINISH")
    return END if next_node == "FINISH" else next_node


def build_graph() -> StateGraph:
    """
    Hub-and-spoke topology: supervisor is the hub, agents are spokes.

      START → supervisor
              ├─→ researcher → supervisor
              ├─→ analyst    → supervisor
              ├─→ writer     → supervisor
              └─→ END

    Every agent always returns to the supervisor after completing.
    The supervisor alone decides what happens next.
    """
    graph = StateGraph(BlogState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("writer", writer_node)

    # Supervisor is the single entry point
    graph.add_edge(START, "supervisor")

    # Every agent reports back to supervisor after completing
    graph.add_edge("researcher", "supervisor")
    graph.add_edge("analyst", "supervisor")
    graph.add_edge("writer", "supervisor")

    # Supervisor decides what happens next (dispatch agent or END)
    graph.add_conditional_edges("supervisor", route_after_supervisor)

    return graph.compile()

