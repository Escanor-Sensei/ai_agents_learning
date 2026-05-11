"""
Agent Core — agent/core.py

Builds and returns the compiled blog generation graph.

Mirrors phase2's core.py pattern:
  phase2 → build_agent() returned (agent, tools, model)
  phase3 → build_graph() returns the compiled StateGraph

Nothing here knows about HTTP, sessions, or user input — pure construction.

.NET analogy: This is the factory method / DI registration.
  build_graph() = builder.Services.AddScoped<IBlogService, BlogGraphService>()
"""

from agent.supervisor import build_graph

# Compile once at import time — graph topology is fixed, no need to rebuild per request.
# .NET analogy: singleton service registered at startup, reused across all requests.
_graph = build_graph()


def get_graph():
    """Returns the compiled blog generation graph."""
    return _graph
