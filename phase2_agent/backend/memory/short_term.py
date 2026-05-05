"""
Short-Term Memory — memory/short_term.py

Uses LangGraph's MemorySaver to persist conversation history in RAM
for the duration of a session.

.NET analogy:
  MemorySaver  ≈  IMemoryCache — fast, in-process, lost on restart
  thread_id    ≈  session ID / correlation ID that scopes the memory
  checkpointer ≈  the middleware that reads/writes state around each invoke()

Lifecycle:
  - Memory lives as long as the process runs
  - Each unique thread_id = isolated conversation (like separate browser tabs)
  - On process restart, all memory is lost (that's why it's "short-term")
"""

from langgraph.checkpoint.memory import MemorySaver


def create_memory() -> MemorySaver:
    """
    Creates and returns a MemorySaver instance.
    Pass this as `checkpointer` when building the agent.
    """
    return MemorySaver()


def build_config(thread_id: str) -> dict:
    """
    Builds the config dict LangGraph needs to scope memory to a session.
    Pass this as `config` on every agent.invoke() call.

    .NET analogy: like passing a correlationId through your middleware pipeline
    so each request reads/writes to the right session slot.
    """
    return {"configurable": {"thread_id": thread_id}}
