"""
=============================================================================
DAY 3 - FILE 08: REFERENCE SOLUTION — Tool Use + Memory Agent (LangChain)
=============================================================================

LangChain conversion of the raw Gemini API implementation.
=============================================================================
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

load_dotenv()

MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")


# ---- MEMORY STORE ----
class MemoryStore:
    def __init__(self, file_path: str = None):
        self.file_path = file_path or os.path.join(os.path.dirname(__file__), "memory_store_task.json")
        self._load()

    def _load(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.store = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.store = {}

    def _save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.store, f, indent=2)

    def save(self, key: str, value: str) -> str:
        self.store[key] = {
            "value": value,
            "saved_at": datetime.now().isoformat()
        }
        self._save()
        return f"Saved: {key} = {value}"

    def search(self, query: str) -> str:
        if not self.store:
            return "No memories stored yet."
        query_lower = query.lower()
        matches = []
        for key, data in self.store.items():
            value = data["value"] if isinstance(data, dict) else str(data)
            if query_lower in key.lower() or query_lower in value.lower():
                matches.append(f"{key}: {value}")

        if matches:
            return "Found:\n" + "\n".join(matches)

        all_items = [f"{k}: {d['value'] if isinstance(d, dict) else d}" for k, d in self.store.items()]
        return "No exact match. All memories:\n" + "\n".join(all_items)

    def list_all(self) -> str:
        if not self.store:
            return "No memories stored yet."
        items = [f"{k}: {d['value'] if isinstance(d, dict) else d}" for k, d in self.store.items()]
        return "All memories:\n" + "\n".join(items)


memory = MemoryStore()


# ---- TOOLS ----
@tool
def calculator(expression: str) -> str:
    """Calculate a math expression. Input: a Python expression like '2 + 3'."""
    try:
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return "Error: only numeric expressions allowed"
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"


@tool
def memory_save(key: str, value: str) -> str:
    """Save an important fact to long-term memory. Use this when the user shares personal info, preferences, or asks you to remember something. key: short label like 'user_name'. value: the fact to store."""
    return memory.save(key, value)


@tool
def memory_search(query: str) -> str:
    """Search long-term memory for previously stored facts. Use this when answering questions about the user or recalling past information."""
    return memory.search(query)


@tool
def memory_list() -> str:
    """List all stored memories. Use when user asks 'what do you know about me?'"""
    return memory.list_all()


# ---- LLM + AGENT SETUP ----
TOOLS = [calculator, memory_save, memory_search, memory_list]

SYSTEM_PROMPT = (
    "You are a helpful assistant with memory. "
    "Use memory_save to store important user facts. "
    "Use memory_search before answering personal questions. "
    "Be concise."
)


def create_agent():
    llm = ChatOllama(model=MODEL_NAME)
    agent = create_react_agent(llm, TOOLS, prompt=SYSTEM_PROMPT)
    return agent


# ---- REFLECTION ----
def reflect_on_answer(query: str, answer: str) -> tuple:
    llm = ChatOllama(model=MODEL_NAME)
    eval_prompt = f"""Grade this answer 1-10.
Question: {query}
Answer: {answer}

Criteria: accuracy, completeness, clarity, specificity.
Format:
SCORE: <1-10>
CRITIQUE: <what needs improvement>"""

    response = llm.invoke([HumanMessage(content=eval_prompt)])
    text = response.content

    score = 5
    critique = text
    for line in text.split("\n"):
        line = line.strip()
        if line.upper().startswith("SCORE:"):
            try:
                score = int(line.split(":")[1].strip().split("/")[0].strip())
                score = max(1, min(10, score))
            except (ValueError, IndexError):
                score = 5
        elif line.upper().startswith("CRITIQUE:"):
            critique = line.split(":", 1)[1].strip()

    return score, critique


# ---- AGENT LOOP ----
def run_agent_turn(agent, message: str) -> str:
    """Run one agent turn. Returns the final response text."""
    result = agent.invoke({"messages": [HumanMessage(content=message)]})
    # Get the last AI message
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            return msg.content
    return "No response."


def run_with_reflection(query: str, agent, max_attempts: int = 3, min_score: int = 7) -> str:
    """Run agent with reflection loop."""
    critique = ""
    answer = ""
    for attempt in range(1, max_attempts + 1):
        msg = query
        if critique:
            msg = f"{query}\n\n[Previous feedback: {critique}. Please improve your answer.]"

        answer = run_agent_turn(agent, msg)
        print(f"  [Attempt {attempt}] Answer: {answer[:100]}...")

        score, critique = reflect_on_answer(query, answer)
        print(f"  [Attempt {attempt}] Score: {score}/10")

        if score >= min_score:
            print(f"  ✓ Accepted (score {score} >= {min_score})")
            return answer

    print(f"  ✗ Max attempts reached. Returning last answer.")
    return answer


# ---- TEST ----
if __name__ == "__main__":
    # Clean slate
    memory.store = {}
    memory._save()

    agent = create_agent()

    print("=" * 60)
    print("CONVERSATION 1: Store facts")
    print("=" * 60)

    print("\nYou: My name is Nihal and my lucky number is 7. Remember this.")
    response = run_agent_turn(agent, "My name is Nihal and my lucky number is 7. Remember this.")
    print(f"Bot: {response[:200]}")

    print("\nYou: What's my lucky number times 6?")
    response = run_agent_turn(agent, "What's my lucky number times 6?")
    print(f"Bot: {response[:200]}")
    print(f"Expected: 42")

    print("\n\n" + "=" * 60)
    print("CONVERSATION 2: New session — long-term memory persists")
    print("=" * 60)

    agent = create_agent()  # New agent = reset short-term memory

    print("\nYou: What do you remember about me?")
    response = run_agent_turn(agent, "What do you remember about me?")
    print(f"Bot: {response[:200]}")
    print(f"Expected: Should find name=Nihal, lucky_number=7")

    print("\n\n" + "=" * 60)
    print("TEST: Reflection")
    print("=" * 60)

    agent = create_agent()
    answer = run_with_reflection(
        "Explain what an AI agent is in exactly 3 bullet points",
        agent
    )
    print(f"\nFinal: {answer[:300]}")

    print("\n\n--- Stored memories ---")
    print(memory.list_all())
