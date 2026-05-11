"""
Analyst Agent — agent/analyst.py

Role: Analyze research notes and extract a logical blog outline.
Output: Structured outline written into state["outline"].

Concept: This node reads from a field the Researcher already filled
(research_notes) — this is how agents chain in a StateGraph without
calling each other directly. The state is the handoff mechanism.
"""

from langchain_core.messages import SystemMessage, HumanMessage

from agent.state import BlogState
from agent.llm import get_llm

_llm = get_llm()

_SYSTEM = """You are an analytical writer. Given research notes on a topic, produce a clear blog outline.
The outline must have: a title, an introduction hook, 3-4 main sections with key points per section,
and a conclusion angle. Be specific — the writer will use this outline directly."""


def analyst_node(state: BlogState) -> dict:
    """
    LangGraph node: reads state["research_notes"], writes state["outline"].

    On a re-route: supervisor_feedback tells the analyst what was wrong
    with the previous outline so it can restructure accordingly.
    """
    feedback = state.get("supervisor_feedback", "")
    feedback_section = (
        f"\n\nSupervisor feedback from previous attempt — fix these issues in the outline:\n{feedback}"
        if feedback else ""
    )
    response = _llm.invoke([
        SystemMessage(content=_SYSTEM),
        HumanMessage(content=(
            f"Topic: {state['topic']}\n\n"
            f"Research Notes:\n{state['research_notes']}\n\n"
            f"Produce a structured blog outline from these notes.{feedback_section}"
        )),
    ])
    return {"outline": response.content, "supervisor_feedback": ""}
