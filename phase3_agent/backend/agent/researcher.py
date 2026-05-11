"""
Researcher Agent — agent/researcher.py

Role: Given a topic, gather and summarize relevant information.
Output: Structured research notes written into state["research_notes"].

Concept: This is a plain LLM call wrapped as a LangGraph node function.
A node function always receives the full BlogState and returns a dict
with only the keys it wants to update — LangGraph merges the rest.
"""

from langchain_core.messages import SystemMessage, HumanMessage

from agent.state import BlogState
from agent.llm import get_llm

_llm = get_llm()

_SYSTEM = """You are a research specialist. Given a topic, produce concise, factual research notes.
Cover: key definitions, main use cases, trade-offs, and real-world examples.
Format as bullet points grouped under short headings. Be thorough but avoid fluff."""


def researcher_node(state: BlogState) -> dict:
    """
    LangGraph node: reads state["topic"], writes state["research_notes"].

    On a re-route: supervisor_feedback is injected into the prompt so the
    researcher knows exactly what was missing and improves its output.
    On first run: supervisor_feedback is empty, so the prompt is clean.
    """
    feedback = state.get("supervisor_feedback", "")
    feedback_section = (
        f"\n\nSupervisor feedback from previous attempt — address these gaps:\n{feedback}"
        if feedback else ""
    )
    response = _llm.invoke([
        SystemMessage(content=_SYSTEM),
        HumanMessage(content=f"Research this topic thoroughly: {state['topic']}{feedback_section}"),
    ])
    return {"research_notes": response.content, "supervisor_feedback": ""}
