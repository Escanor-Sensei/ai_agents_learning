"""
=============================================================================
DAY 3 - FILE 06 (TASK): Build an Agent with Tools + Memory
=============================================================================

INSTRUCTIONS:
Extend the Day 1/2 agent with:
1. Short-term memory (conversation context across turns)
2. Long-term memory (persistent facts saved to JSON file)
3. Self-reflection (evaluate and retry poor answers)

Your agent must handle these test conversations:

Conversation 1:
  "My name is Nihal and my lucky number is 7. Remember this."
  "What's my lucky number times 6?"
  → Should remember name and number from previous turn (short-term)
  → Should save facts to long-term memory

Conversation 2 (NEW session — short-term memory is gone):
  "What do you remember about me?"
  → Should retrieve name and lucky number from LONG-TERM memory

Test with reflection:
  "Explain what an AI agent is in exactly 3 bullet points"
  → Should self-evaluate, and retry if not exactly 3 bullets

Requirements:
1. Build a MemoryStore class (save, search, list_all) backed by JSON
2. Integrate memory_save and memory_search as agent tools
3. Add a reflect_on_answer() function that grades the answer 1-10
4. If score < 7, retry with the critique (max 3 attempts)
5. Support multi-turn conversations (short-term memory)

=============================================================================
HINTS (read ONE AT A TIME, only if stuck):
=============================================================================

HINT 1: MemoryStore is just a dict saved to a JSON file.
         class MemoryStore:
             def save(key, value) → write to file
             def search(query) → keyword match
             def list_all() → return everything

HINT 2: For short-term memory, keep a `contents` list (Gemini message format).
         Each turn: append user message → call API → append model response.
         Same list for the whole conversation.

HINT 3: For reflection, after getting the agent's answer:
         score, critique = evaluate(query, answer)
         if score < 7:
             answer = regenerate(query, critique)

HINT 4: Wire memory tools into the Gemini function calling:
         functionDeclarations for memory_save, memory_search, memory_list
         Handle functionCall responses by dispatching to MemoryStore methods

=============================================================================
STARTER CODE (fill in the blanks):
=============================================================================
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

try:
    import requests
except ImportError:
    os.system("pip install requests")
    import requests

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"


# ---- MEMORY STORE (YOU BUILD THIS) ----
class MemoryStore:
    def __init__(self, file_path: str = None):
        self.file_path = file_path or os.path.join(os.path.dirname(__file__), "memory_store_task.json")
        # TODO: Load existing data from file
        pass
    
    def save(self, key: str, value: str) -> str:
        """Save a fact to long-term memory."""
        # TODO: Store key-value pair with timestamp, write to file
        pass
    
    def search(self, query: str) -> str:
        """Search for facts matching a keyword."""
        # TODO: Search through stored facts by keyword
        pass
    
    def list_all(self) -> str:
        """List all stored facts."""
        # TODO: Return all stored key-value pairs
        pass


# ---- TOOLS ----
memory = MemoryStore()

def calculator(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"


# ---- LLM HELPERS ----
def call_llm_simple(prompt: str) -> str:
    """Simple text generation (no function calling)."""
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    response = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, json=body)
    if response.status_code != 200:
        raise Exception(f"API error {response.status_code}: {response.text}")
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


def call_llm_with_tools(contents: list) -> dict:
    """Call Gemini with function calling enabled."""
    # TODO: Build the request body with:
    # - contents (conversation history)
    # - tools (functionDeclarations for calculator, memory_save, memory_search, memory_list)
    # - systemInstruction
    pass


# ---- REFLECTION (YOU BUILD THIS) ----
def reflect_on_answer(query: str, answer: str) -> tuple:
    """
    Evaluate answer quality. Returns (score, critique).
    """
    # TODO: Call LLM with evaluation prompt
    # Return (score: int, critique: str)
    pass


# ---- AGENT LOOP WITH MEMORY + REFLECTION (YOU BUILD THIS) ----
def run_agent_turn(contents: list, user_message: str) -> tuple:
    """
    Run one turn: add user message, call agent loop, return (response, updated_contents).
    """
    # TODO:
    # 1. Add user message to contents
    # 2. Run the agent loop (call LLM, handle tool calls, repeat until text response)
    # 3. Return the text response and updated contents
    pass


def run_with_reflection(query: str, contents: list) -> tuple:
    """
    Run agent with reflection. Retry if score < 7.
    """
    # TODO:
    # 1. Run run_agent_turn to get initial answer
    # 2. Call reflect_on_answer to evaluate
    # 3. If score < 7 and attempts < 3: retry with critique feedback
    # 4. Return (best_answer, updated_contents)
    pass


# ---- TEST ----
if __name__ == "__main__":
    # Clear memory for clean test
    if os.path.exists(os.path.join(os.path.dirname(__file__), "memory_store_task.json")):
        os.remove(os.path.join(os.path.dirname(__file__), "memory_store_task.json"))
    
    print("=" * 60)
    print("CONVERSATION 1: Store facts")
    print("=" * 60)
    
    contents = []
    
    msgs_1 = [
        "My name is Nihal and my lucky number is 7. Remember this.",
        "What's my lucky number times 6?",
    ]
    
    for msg in msgs_1:
        print(f"\nYou: {msg}")
        response, contents = run_agent_turn(contents, msg)
        print(f"Bot: {response[:200]}")
    
    print(f"\nExpected: Name saved to memory, 7 * 6 = 42")
    
    print("\n\n" + "=" * 60)
    print("CONVERSATION 2: New session (long-term memory should persist)")
    print("=" * 60)
    
    contents = []  # New session — short-term memory cleared!
    
    response, contents = run_agent_turn(contents, "What do you remember about me?")
    print(f"\nYou: What do you remember about me?")
    print(f"Bot: {response[:200]}")
    print(f"\nExpected: Should find name=Nihal, lucky_number=7 from long-term memory")
    
    print("\n\n" + "=" * 60)
    print("TEST: Reflection")
    print("=" * 60)
    
    contents = []
    answer, contents = run_with_reflection(
        "Explain what an AI agent is in exactly 3 bullet points",
        contents
    )
    print(f"\nFinal answer: {answer[:300]}")
