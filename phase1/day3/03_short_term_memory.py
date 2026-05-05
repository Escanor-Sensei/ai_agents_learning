"""
=============================================================================
DAY 3 - FILE 03: SHORT-TERM MEMORY (Conversation Memory)
=============================================================================

CONCEPT:
- Without memory, every LLM call is a blank slate — it forgets everything.
- Short-term memory = resend previous messages so the LLM has context.
- The LLM doesn't "remember" — we just replay the conversation each call.
- Framework handles this with MemorySaver + thread_id.
- More messages = better context, BUT more tokens = more cost.

ANALOGY FOR .NET DEVS:
- Short-term memory = HttpContext.Session. Exists during the session, gone after.
- No memory = every request is a new anonymous user.
- thread_id = session cookie. Different threads = different sessions.
=============================================================================
"""

import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langgraph")
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from _tools import calculator, search_web
from langchain_ollama import ChatOllama

load_dotenv()

llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"))
tools = [calculator, search_web]


# =========================
# STEP 1: WITHOUT memory (each call is independent)
# =========================

print("=" * 60)
print("WITHOUT MEMORY: Agent forgets everything")
print("=" * 60)

agent_no_memory = create_agent(model=llm, tools=tools)

result1 = agent_no_memory.invoke({"messages": [("human", "My name is Nihal and my favorite number is 42")]})
print(f"\n  Turn 1: {result1['messages'][-1].content[:150]}")

result2 = agent_no_memory.invoke({"messages": [("human", "What is my favorite number times 10?")]})
print(f"  Turn 2: {result2['messages'][-1].content[:150]}")
print("\n  -> Agent has NO IDEA what your number is! Each call is independent.\n")


# =========================
# STEP 2: WITH memory (MemorySaver + thread_id)
# =========================

print("=" * 60)
print("WITH MEMORY: Agent remembers the conversation")
print("=" * 60)

memory = MemorySaver()
agent_with_memory = create_agent(model=llm, tools=tools, checkpointer=memory)
config = {"configurable": {"thread_id": "conversation-1"}}

result1 = agent_with_memory.invoke(
    {"messages": [("human", "My name is Nihal and my favorite number is 42")]},
    config=config
)
print(f"\n  Turn 1: {result1['messages'][-1].content[:150]}")

result2 = agent_with_memory.invoke(
    {"messages": [("human", "What is my favorite number times 10?")]},
    config=config
)
print(f"  Turn 2: {result2['messages'][-1].content[:150]}")

result3 = agent_with_memory.invoke(
    {"messages": [("human", "What's my name?")]},
    config=config
)
print(f"  Turn 3: {result3['messages'][-1].content[:150]}")


# =========================
# STEP 3: Different threads = different memory
# =========================

print("\n\n" + "=" * 60)
print("SEPARATE THREADS: Different thread_ids = isolated memory")
print("=" * 60)

config_a = {"configurable": {"thread_id": "thread-A"}}
config_b = {"configurable": {"thread_id": "thread-B"}}

agent_with_memory.invoke({"messages": [("human", "The secret code is ALPHA-7")]}, config=config_a)
agent_with_memory.invoke({"messages": [("human", "The secret code is BETA-9")]}, config=config_b)

result_a = agent_with_memory.invoke({"messages": [("human", "What's the secret code?")]}, config=config_a)
result_b = agent_with_memory.invoke({"messages": [("human", "What's the secret code?")]}, config=config_b)

print(f"\n  Thread A: {result_a['messages'][-1].content[:100]}")
print(f"  Thread B: {result_b['messages'][-1].content[:100]}")
print("\n  -> Each thread has isolated memory - like separate browser sessions")


# =========================
# STEP 4: Inspect what's stored
# =========================

print("\n\n" + "=" * 60)
print("UNDER THE HOOD: What's in the memory?")
print("=" * 60)

state = agent_with_memory.get_state(config_a)
print(f"\n  Thread A has {len(state.values['messages'])} messages:")
for i, msg in enumerate(state.values["messages"]):
    role = msg.__class__.__name__
    content = str(msg.content)[:80] if hasattr(msg, "content") and msg.content else "(no content)"
    print(f"    [{i}] {role}: {content}")


print("""
=============================================================================
DEEP THEORY: Short-Term Memory Types
=============================================================================

1. MEMORY IS JUST A LIST
   Under the hood: self.messages = []
   Each turn: append user msg + append AI response.
   Next call: send ALL stored messages + new message to the LLM.
   "Memory" = "which old messages get included in the API call."

2. THE GROWTH PROBLEM
   20 turns × 100 chars each = ~1000+ tokens just for history.
   Cost and latency grow linearly with conversation length.
   "Even if you CAN send 1M tokens, you probably SHOULDN'T."

3. TYPES OF SHORT-TERM MEMORY
   ┌─────────────────────────┬──────────────────────────────────┐
   │ Type                    │ How it works                     │
   ├─────────────────────────┼──────────────────────────────────┤
   │ Buffer (all messages)   │ Keep everything. Simple but      │
   │                         │ grows forever. Hits token limit.  │
   ├─────────────────────────┼──────────────────────────────────┤
   │ Window (last N turns)   │ Keep recent context. Fixed size. │
   │                         │ Forgets old info.                 │
   ├─────────────────────────┼──────────────────────────────────┤
   │ Summary (compressed)    │ Periodically summarize old msgs. │
   │                         │ Keeps gist, loses details.        │
   ├─────────────────────────┼──────────────────────────────────┤
   │ Token-limited           │ Keep messages until near limit.  │
   │                         │ Most precise budget control.      │
   └─────────────────────────┴──────────────────────────────────┘

   Framework equivalents:
   - Buffer: MemorySaver (what we used above)
   - Window: ConversationBufferWindowMemory
   - Summary: ConversationSummaryMemory
   
   ALL are variations of "which messages to include in the API call."

=============================================================================
""")
