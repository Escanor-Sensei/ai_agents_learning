"""
Writer Agent — agent/writer.py

Role: Convert the analyst's outline into a well-written ~500 word blog post.
Output: Final blog post written into state["blog_post"].

Concept: The writer is the last specialized agent in the chain.
It has access to both the outline AND the raw research notes so it can
add depth beyond just the outline structure.
"""

from langchain_core.messages import SystemMessage, HumanMessage

from agent.state import BlogState
from agent.llm import get_llm

_llm = get_llm()

_SYSTEM = """You are a professional technical blogger. Write a clear, engaging blog post (~500 words).
Follow the provided outline exactly. Use the research notes for factual depth.
Write in a direct, conversational tone. Use short paragraphs. Include a strong opening and a clear conclusion."""


def writer_node(state: BlogState) -> dict:
    """
    LangGraph node: reads state["outline"] + state["research_notes"], writes state["blog_post"].

    On a re-route: supervisor_feedback tells the writer exactly what to fix
    in the blog post (tone, structure, missing points, word count, etc.).
    """
    feedback = state.get("supervisor_feedback", "")
    feedback_section = (
        f"\n\nSupervisor feedback from previous attempt — address every point:\n{feedback}"
        if feedback else ""
    )
    response = _llm.invoke([
        SystemMessage(content=_SYSTEM),
        HumanMessage(content=(
            f"Topic: {state['topic']}\n\n"
            f"Outline:\n{state['outline']}\n\n"
            f"Research Notes (for depth):\n{state['research_notes']}\n\n"
            f"Write the full blog post now.{feedback_section}"
        )),
    ])
    return {"blog_post": response.content, "supervisor_feedback": ""}
