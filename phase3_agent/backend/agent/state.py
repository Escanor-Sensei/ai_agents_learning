"""
Blog State — agent/state.py

Defines the shared state that flows between all agents in the graph.

Concept: In a multi-agent StateGraph, every node (agent) reads from and
writes to this single state object. It's how agents "talk" to each other
without calling each other directly — the Supervisor just checks this state
to decide what to do next.

Analogy from phase2:
  phase2 → state was just {"messages": [...]}  (LangGraph managed it)
  phase3 → we define our own typed state with domain-specific fields
"""

from typing import TypedDict, Literal


class BlogState(TypedDict):
    topic: str                        # Input: the blog topic from the user
    research_notes: str               # Researcher output: raw gathered info
    outline: str                      # Analyst output: structured key points
    blog_post: str                    # Writer output: final blog content
    supervisor_feedback: str          # Supervisor's feedback to the re-routed node
    next_node: str                    # Supervisor's routing decision: researcher | analyst | writer | FINISH
    retry_count: int                  # Guards against infinite re-routing loops
