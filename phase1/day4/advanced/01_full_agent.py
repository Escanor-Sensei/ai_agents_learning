"""
=============================================================================
DAY 4 - FILE 01: THE COMPLETE SMART TASK AGENT (Framework Version)
=============================================================================

CONCEPT (5 lines):
- Days 1-3 built individual pieces: tools, planning, memory, reflection.
- Today we combine EVERYTHING into one robust agent system.
- This is the "production-ready" version (as close as learning code gets).
- One agent with: 5+ tools, conversation memory, long-term memory, reflection.
- This is what a real-world LangGraph agent looks like.

ARCHITECTURE:
  Query → [Search Memory] → [Plan] → [Execute with Tools] → [Reflect] → Answer
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

load_dotenv()

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))

# Long-term memory file
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "agent_memory.json")


# =========================
# STEP 1: Long-term memory helpers
# =========================

def _load_lt_memory() -> dict:
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _save_lt_memory(store: dict):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2)


# =========================
# STEP 2: All tools
# =========================

@tool
def calculator(expression: str) -> str:
    """Calculate a math expression. Input: a valid Python expression like '2 + 3 * 4'. Returns the numeric result."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

@tool
def get_word_length(word: str) -> str:
    """Count characters in a word or phrase. Input: a word or phrase. Returns the count."""
    return str(len(word))

@tool
def search_web(query: str) -> str:
    """Search the web for information. Input: a search query string. Returns relevant results."""
    SEARCH_DB = {
        "python": "Python is a high-level programming language created by Guido van Rossum in 1991. Used for web dev, AI, data science. Latest: 3.12.",
        "langchain": "LangChain is a framework for building LLM applications. Supports agents, chains, memory. Created by Harrison Chase in 2022.",
        "machine learning": "Machine learning is a subset of AI where systems learn from data. Types: supervised, unsupervised, reinforcement learning.",
        "react pattern": "ReAct (Reasoning + Acting) is an agent pattern where LLMs alternate between thinking and taking actions.",
        "weather": "Current weather: 72°F (22°C), partly cloudy, humidity 45%.",
        "population": "World population: approximately 8.1 billion as of 2024.",
    }
    for key, val in SEARCH_DB.items():
        if key in query.lower():
            return val
    return f"No results for: {query}"

@tool
def read_file(file_path: str) -> str:
    """Read a text file. Input: filename like 'notes.txt'. Returns file contents."""
    try:
        safe_path = os.path.basename(file_path)
        # Search in day4, day2, and parent directories
        search_dirs = [
            os.path.dirname(__file__),
            os.path.join(os.path.dirname(__file__), "..", "day2"),
        ]
        for dir_path in search_dirs:
            full_path = os.path.join(dir_path, safe_path)
            if os.path.exists(full_path):
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                return content[:2000]
        return f"Error: File '{safe_path}' not found."
    except Exception as e:
        return f"Error: {e}"

@tool
def get_current_time(format: str = "full") -> str:
    """Get current date/time. Input: 'full', 'date', or 'time'."""
    now = datetime.now()
    if format == "date":
        return now.strftime("%Y-%m-%d")
    elif format == "time":
        return now.strftime("%H:%M:%S")
    return now.strftime("%Y-%m-%d %H:%M:%S")

@tool
def memory_save(key: str, value: str) -> str:
    """Save a fact to persistent long-term memory. Input: key (label like 'user_name'), value (fact like 'Nihal'). Use when user shares important info."""
    store = _load_lt_memory()
    store[key] = {"value": value, "saved_at": datetime.now().isoformat()}
    _save_lt_memory(store)
    return f"Saved to memory: {key} = {value}"

@tool
def memory_search(query: str) -> str:
    """Search long-term memory for stored facts. Input: keyword to search. Use before answering personal questions."""
    store = _load_lt_memory()
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
    all_items = [f"{k}: {d['value'] if isinstance(d, dict) else d}" for k, d in store.items()]
    return "No exact match. All memories:\n" + "\n".join(all_items)


# =========================
# STEP 3: Create the FULL agent
# =========================

all_tools = [
    calculator, get_word_length, search_web, read_file,
    get_current_time, memory_save, memory_search,
]

checkpointer = MemorySaver()

full_agent = create_react_agent(
    model=llm,
    tools=all_tools,
    checkpointer=checkpointer,
)


# =========================
# STEP 4: Reflection wrapper
# =========================

def evaluate_answer(query: str, answer: str) -> tuple:
    """Use LLM to evaluate answer quality."""
    eval_prompt = f"""Grade this answer 1-10. Be strict.
Question: {query}
Answer: {answer}
Criteria: accuracy, completeness, clarity.
Format:
SCORE: <1-10>
CRITIQUE: <feedback>"""
    
    response = llm.invoke(eval_prompt)
    text = response.content
    
    score = 5
    critique = text
    for line in text.split("\n"):
        line = line.strip()
        if line.upper().startswith("SCORE:"):
            try:
                score = int(line.split(":")[1].strip().split("/")[0].strip())
            except (ValueError, IndexError):
                score = 5
        elif line.upper().startswith("CRITIQUE:"):
            critique = line.split(":", 1)[1].strip()
    
    return score, critique


def run_with_reflection(query: str, config: dict, max_attempts: int = 2) -> str:
    """Run the agent with optional reflection."""
    
    for attempt in range(1, max_attempts + 1):
        msg = query
        if attempt > 1:
            msg = f"{query}\n\n[Feedback from review: {critique}. Please improve your answer.]"
        
        result = full_agent.invoke(
            {"messages": [("human", msg)]},
            config=config,
        )
        answer = str(result["messages"][-1].content)
        
        if max_attempts == 1:
            return answer
        
        score, critique = evaluate_answer(query, answer)
        print(f"  [Attempt {attempt}] Score: {score}/10")
        
        if score >= 7:
            return answer
    
    return answer


# =========================
# STEP 5: High-level API
# =========================

class SmartTaskAgent:
    """The complete Smart Task Agent — everything combined."""
    
    def __init__(self):
        self.thread_counter = 0
    
    def new_session(self) -> dict:
        """Start a new conversation session."""
        self.thread_counter += 1
        return {"configurable": {"thread_id": f"session-{self.thread_counter}"}}
    
    def chat(self, query: str, config: dict, reflect: bool = False) -> str:
        """Send a message and get a response."""
        max_attempts = 2 if reflect else 1
        return run_with_reflection(query, config, max_attempts)
    
    def get_memories(self) -> dict:
        """Get all stored long-term memories."""
        return _load_lt_memory()


# =========================
# STEP 6: Test the complete agent
# =========================

if __name__ == "__main__":
    agent = SmartTaskAgent()
    
    # Session 1: Multi-turn with memory
    print("=" * 60)
    print("SESSION 1: Full capabilities demo")
    print("=" * 60)
    
    config = agent.new_session()
    
    queries = [
        ("My name is Nihal. I'm learning about AI agents. Remember this.", False),
        ("What is 42 * 17?", False),
        ("Search for information about LangChain", False),
        ("Read the file notes.txt and tell me the average response time", False),
        ("What time is it?", False),
        ("What's my name? Check your memory.", False),
    ]
    
    for query, reflect in queries:
        print(f"\nYou: {query}")
        answer = agent.chat(query, config, reflect=reflect)
        print(f"Bot: {str(answer)[:200]}")
    
    # Session 2: Prove long-term memory works
    print("\n\n" + "=" * 60)
    print("SESSION 2: New session — long-term memory persists")
    print("=" * 60)
    
    config2 = agent.new_session()
    
    print("\nYou: What do you remember about me?")
    answer = agent.chat("What do you remember about me? Search your memory.", config2)
    print(f"Bot: {str(answer)[:200]}")
    
    # Session 3: Reflection
    print("\n\n" + "=" * 60)
    print("SESSION 3: With reflection")
    print("=" * 60)
    
    config3 = agent.new_session()
    
    print("\nYou: Explain AI agents vs chatbots in exactly 3 bullet points")
    answer = agent.chat(
        "Explain AI agents vs chatbots in exactly 3 bullet points",
        config3,
        reflect=True
    )
    print(f"Bot: {str(answer)[:400]}")
    
    # Show architecture
    print("\n\n" + "=" * 60)
    print("ARCHITECTURE: What we built")
    print("=" * 60)
    print("""
    ┌─────────────────────────────────────────────────────────┐
    │                SMART TASK AGENT (v4.0)                   │
    ├─────────────────────────────────────────────────────────┤
    │                                                         │
    │  User Query                                             │
    │      │                                                  │
    │      ▼                                                  │
    │  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │
    │  │ Short-   │  │ Long-term    │  │ Tools:           │  │
    │  │ term     │  │ Memory       │  │ - calculator     │  │
    │  │ Memory   │  │ (JSON file)  │  │ - search_web     │  │
    │  │ (thread) │  │              │  │ - read_file      │  │
    │  └────┬─────┘  └──────┬───────┘  │ - get_time       │  │
    │       │               │          │ - word_length    │  │
    │       ▼               ▼          │ - memory_save    │  │
    │  ┌────────────────────────────┐  │ - memory_search  │  │
    │  │    LLM (Gemini)            │──│                  │  │
    │  │    ReAct Loop              │  └──────────────────┘  │
    │  │    (think → act → observe) │                         │
    │  └─────────────┬──────────────┘                         │
    │                │                                        │
    │                ▼                                        │
    │  ┌──────────────────────┐                               │
    │  │ Reflection (optional)│                               │
    │  │ Score < 7? → Retry   │                               │
    │  └──────────┬───────────┘                               │
    │             │                                           │
    │             ▼                                           │
    │         Answer                                          │
    └─────────────────────────────────────────────────────────┘
    """)

    # KEY OBSERVATION:
    # - Everything from Days 1-3 in ONE agent: tools, memory, reflection
    # - ~100 lines of application code (framework handles the rest)
    # - But do you understand what the framework is hiding?
    #
    # → File 02: Same agent, ZERO frameworks — raw Gemini API only
