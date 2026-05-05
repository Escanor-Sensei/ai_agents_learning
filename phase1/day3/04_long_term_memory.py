"""
=============================================================================
DAY 3 - FILE 04: LONG-TERM MEMORY (Persistent Memory)
=============================================================================

CONCEPT:
- Short-term memory (file 03) dies when the process exits.
- Long-term memory persists across conversations — stored on disk.
- The agent gets memory_save and memory_search tools — it decides when to use them.
- Two memory systems work together: short-term (session) + long-term (disk).

ANALOGY FOR .NET DEVS:
- Short-term = HttpContext.Session (dies with the process)
- Long-term = database/Redis (survives restarts)
=============================================================================
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from _tools import calculator

load_dotenv()

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory_store.json")


# =========================
# STEP 1: Persistent memory store (JSON file)
# =========================

def load_memory_store() -> dict:
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_memory_store(store: dict):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2)


# =========================
# STEP 2: Memory tools (agent calls these)
# =========================

@tool
def memory_save(key: str, value: str) -> str:
    """Save a fact to long-term memory. Input: key (short label like 'user_name'), value (the fact). Use when the user tells you something worth remembering."""
    store = load_memory_store()
    store[key] = {"value": value, "saved_at": datetime.now().isoformat()}
    save_memory_store(store)
    return f"Saved: {key} = {value}"


@tool
def memory_search(query: str) -> str:
    """Search long-term memory for relevant facts. Input: keyword or topic. Use when the user asks about something mentioned before."""
    store = load_memory_store()
    if not store:
        return "No memories stored yet."
    query_lower = query.lower()
    matches = []
    for key, data in store.items():
        value = data["value"] if isinstance(data, dict) else str(data)
        if query_lower in key.lower() or query_lower in value.lower():
            matches.append(f"{key}: {value}")
    if matches:
        return "Found in memory:\n" + "\n".join(matches)
    all_mems = [f"{k}: {v['value'] if isinstance(v, dict) else v}" for k, v in store.items()]
    return "No exact match. All memories:\n" + "\n".join(all_mems)


@tool
def memory_list() -> str:
    """List all facts stored in long-term memory."""
    store = load_memory_store()
    if not store:
        return "No memories stored yet."
    lines = []
    for key, data in store.items():
        value = data["value"] if isinstance(data, dict) else str(data)
        lines.append(f"  {key}: {value}")
    return f"Stored memories ({len(store)}):\n" + "\n".join(lines)


# =========================
# STEP 3: Agent with both memory types
# =========================

checkpointer = MemorySaver()  # Short-term
agent = create_react_agent(
    model=llm,
    tools=[memory_save, memory_search, memory_list, calculator],
    checkpointer=checkpointer,
)


# =========================
# STEP 4: Conversation 1 — teach the agent about yourself
# =========================

print("=" * 60)
print("CONVERSATION 1: Teaching the agent (saves to long-term memory)")
print("=" * 60)

config1 = {"configurable": {"thread_id": "session-1"}}

queries = [
    "My name is Nihal. I'm a software developer. Please remember that.",
    "My favorite programming language is Python. Remember that too.",
    "What do you know about me? Check your memory.",
]

for q in queries:
    print(f"\n  You: {q}")
    result = agent.invoke({"messages": [("human", q)]}, config=config1)
    print(f"  Bot: {str(result['messages'][-1].content)[:200]}")


# =========================
# STEP 5: Conversation 2 — NEW session, but long-term memory survives
# =========================

print("\n\n" + "=" * 60)
print("CONVERSATION 2: New session — long-term memory survives!")
print("=" * 60)

config2 = {"configurable": {"thread_id": "session-2"}}

queries2 = [
    "Do you remember anything about me? Search your memory.",
    "What's my name and what language do I use?",
]

for q in queries2:
    print(f"\n  You: {q}")
    result = agent.invoke({"messages": [("human", q)]}, config=config2)
    print(f"  Bot: {str(result['messages'][-1].content)[:200]}")


# =========================
# STEP 6: Show what's on disk
# =========================

print("\n\n" + "=" * 60)
print("ON DISK: memory_store.json")
print("=" * 60)

store = load_memory_store()
print(json.dumps(store, indent=2))


print("""
=============================================================================
DEEP THEORY: Long-Term Memory & Two-Layer Architecture
=============================================================================

1. TWO MEMORY LAYERS
   ┌─────────────────────────────────┐
   │ SHORT-TERM (MemorySaver)        │  ← Conversation history (RAM)
   │ - "You just said X"             │  ← Dies when process exits
   │ - Managed by thread_id          │  ← Per-conversation
   ├─────────────────────────────────┤
   │ LONG-TERM (memory_store.json)   │  ← Persisted facts (disk)
   │ - "User's name is Nihal"        │  ← Survives restarts
   │ - Searchable by keyword         │  ← Cross-conversation
   └─────────────────────────────────┘

2. RAW MEMORY STORE (What the Framework Hides)
   Under the hood, it's a dict backed by JSON:
     save(key, value) → writes {key: {value, saved_at}}
     search(query)    → keyword match
     list_all()       → dump everything
   Production systems add: access_count, TTL/expiry, relevance scoring.

3. PRODUCTION UPGRADES
   ┌─────────────────────────┬──────────────────────────────────┐
   │ Our version             │ Production version               │
   ├─────────────────────────┼──────────────────────────────────┤
   │ JSON file on disk       │ Vector DB (Pinecone, Weaviate)   │
   │ Keyword matching        │ Embedding/semantic search        │
   │ No expiry               │ TTL/expiry for old memories      │
   │ Simple dict storage     │ Database (Redis, Cosmos)          │
   └─────────────────────────┴──────────────────────────────────┘

=============================================================================
""")
