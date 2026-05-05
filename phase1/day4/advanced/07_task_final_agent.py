"""
=============================================================================
DAY 4 - FILE 07: TASK — Build the Final Smart Task Agent
=============================================================================

YOUR CHALLENGE:
Build a complete SmartTaskAgent class that combines EVERYTHING from 4 days:
- Tools (Day 2)
- Planning (Day 2)
- Memory — short-term + long-term (Day 3)
- Reflection (Day 3)
- Error handling (Day 4)
- Evaluation-ready (Day 4)

The agent should:
1. PLAN: Break complex queries into steps
2. EXECUTE: Run steps using tools, handling errors
3. REFLECT: Check if the answer is good, retry if needed
4. REMEMBER: Save useful results to long-term memory
5. LEARN: Use past memory to improve future answers

This is the capstone. Everything you learned in 4 days goes here.

RULES:
- Raw Python only (requests, json, os)
- No LangChain, no LangGraph
- Fill in the marked sections
- Use the progressive hints if stuck (each unlocks after the previous)
=============================================================================
"""

import os
import json
import time
from datetime import datetime

try:
    import requests
except ImportError:
    os.system("pip install requests")
    import requests

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"


# =========================
# PART 1: Memory Store (from Day 3)
# =========================

class MemoryStore:
    """Persistent memory using a JSON file."""
    
    def __init__(self, filepath: str = None):
        self.filepath = filepath or os.path.join(os.path.dirname(__file__), "agent_memory.json")
        # TODO: Load existing memories from file, or initialize empty dict
        # HINT: self.memories should be a dict loaded from self.filepath
        self.memories = {}  # Replace this
    
    def save(self, key: str, value: str, category: str = "general") -> str:
        """Save a fact to memory."""
        # TODO: Store the memory with timestamp and category
        # TODO: Persist to JSON file
        pass
    
    def search(self, query: str) -> list:
        """Search memories by keyword matching."""
        # TODO: Return list of memories where query words appear in key or value
        pass
    
    def list_all(self) -> list:
        """List all memory keys."""
        # TODO: Return list of all stored memory keys
        pass


# =========================
# PART 2: Tool Definitions
# =========================

def calculator(expression: str) -> str:
    """Safe calculator with input validation."""
    # TODO: Implement with try/except and input sanitization
    # HINT: Check that only math characters are in the expression
    pass

def search_web(query: str) -> str:
    """Simulated web search."""
    # TODO: Simple dictionary-based search simulation
    pass

def read_file_tool(file_path: str) -> str:
    """Safe file reader."""
    # TODO: Read file with path traversal prevention (use os.path.basename)
    pass

def get_current_time(fmt: str = "full") -> str:
    """Get current date/time."""
    # TODO: Return formatted datetime
    pass

# Tool registry: maps name → function
TOOL_FUNCTIONS = {
    # TODO: Map tool names to their functions
    # Also include memory tools: "memory_save", "memory_search", "memory_list"
}

# Tool declarations for Gemini API
TOOL_DECLARATIONS = [
    # TODO: Write the functionDeclarations array for all tools
    # Each needs: name, description, parameters (type, properties, required)
    # HINT: Look at day2/03_raw_tool_registry.py for the format
]


# =========================
# PART 3: Core Agent Functions
# =========================

def call_gemini(contents: list, tools: list = None, system: str = None) -> dict:
    """Call Gemini API with retry and error handling."""
    # TODO: Implement with:
    # - systemInstruction
    # - tools (functionDeclarations) if provided
    # - Retry on 429 with exponential backoff (max 3 retries)
    # - Timeout of 30 seconds
    # HINT: Look at day4/04_error_handling.py for the pattern
    pass


def dispatch_tool(name: str, args: dict) -> str:
    """Route a tool call to the right function with error handling."""
    # TODO: Look up name in TOOL_FUNCTIONS, call it, catch exceptions
    # Return error string if tool not found or throws
    pass


# =========================
# PART 4: The SmartTaskAgent Class
# =========================

class SmartTaskAgent:
    """
    The Final Agent — combines all 4 days of learning.
    
    Capabilities:
    - Tool use (Day 2)
    - Planning (Day 2)
    - Short-term memory via conversation (Day 3)
    - Long-term memory via MemoryStore (Day 3)
    - Reflection (Day 3)
    - Error handling (Day 4)
    """
    
    def __init__(self):
        self.memory = MemoryStore()
        self.conversation = []  # Short-term (current session)
        self.max_iterations = 10
        self.reflection_threshold = 7  # Score 1-10
    
    def plan(self, query: str) -> list:
        """Generate a plan for complex queries."""
        # TODO: Ask Gemini to create a step-by-step plan
        # Return a list of step strings
        # HINT: Use a prompt like "Break this into 2-4 steps: {query}. Return JSON array."
        pass
    
    def execute_step(self, step: str) -> str:
        """Execute a single step using the agent loop."""
        # TODO: Standard agent loop:
        # 1. Send step as user message (with TOOL_DECLARATIONS)
        # 2. If model returns functionCall → dispatch_tool → send result back
        # 3. If model returns text → return it
        # 4. Max iterations check
        # HINT: This is the core loop from day2/03_raw_tool_registry.py
        pass
    
    def reflect(self, query: str, answer: str) -> dict:
        """Self-evaluate the answer quality."""
        # TODO: Ask Gemini to evaluate: "Rate this answer 1-10. SCORE: N REASON: ..."
        # Return {"score": int, "reason": str, "passed": bool}
        # HINT: Look at day3/05_reflection.py for the pattern
        pass
    
    def remember(self, query: str, answer: str):
        """Save useful results to long-term memory."""
        # TODO: Save the query-answer pair to self.memory
        # Only save if the answer seems useful (not an error message)
        pass
    
    def check_memory(self, query: str) -> str:
        """Check if we've answered a similar question before."""
        # TODO: Search self.memory for the query
        # If found, return the cached answer with a note
        # If not found, return None
        pass
    
    def run(self, query: str) -> str:
        """Main entry point — the full pipeline."""
        # TODO: Implement the complete pipeline:
        #
        # 1. Check memory for cached answer
        #    cached = self.check_memory(query)
        #    if cached: return cached
        #
        # 2. Plan
        #    steps = self.plan(query)
        #
        # 3. Execute each step
        #    for step in steps: result = self.execute_step(step)
        #
        # 4. Combine results into final answer
        #
        # 5. Reflect — if score < threshold, retry once
        #    reflection = self.reflect(query, answer)
        #    if not reflection["passed"]:
        #        improved_answer = self.execute_step(
        #            f"Improve this answer: {answer}. Issue: {reflection['reason']}"
        #        )
        #
        # 6. Remember the answer
        #    self.remember(query, final_answer)
        #
        # 7. Return
        pass


# =========================
# PART 5: Test the agent
# =========================
if __name__ == "__main__":
    agent = SmartTaskAgent()
    
    test_queries = [
        "What is 42 * 17?",
        "Search for info about Python and tell me who created it",
        "What is 42 * 17?",  # Should hit memory cache!
    ]
    
    for q in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {q}")
        result = agent.run(q)
        print(f"Answer: {result}")


# =========================
# PROGRESSIVE HINTS (read only when stuck!)
# =========================

"""
HINT 1 — MemoryStore:
    def __init__(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                self.memories = json.load(f)
        else:
            self.memories = {}

HINT 2 — call_gemini:
    body = {"contents": contents}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    if tools:
        body["tools"] = [{"functionDeclarations": tools}]
    for attempt in range(4):
        resp = requests.post(GEMINI_URL, json=body, timeout=30)
        if resp.status_code == 200: return resp.json()
        if resp.status_code == 429: time.sleep(2 ** attempt); continue
        raise Exception(f"API error {resp.status_code}")

HINT 3 — plan():
    prompt = f"Break this into 2-4 actionable steps. Return ONLY a JSON array of strings.\\nTask: {query}"
    result = call_gemini([{"role": "user", "parts": [{"text": prompt}]}])
    text = result["candidates"][0]["content"]["parts"][0]["text"]
    # Parse JSON from the response (strip markdown if needed)
    text = text.strip().strip("```json").strip("```").strip()
    return json.loads(text)

HINT 4 — execute_step() core loop:
    contents = [{"role": "user", "parts": [{"text": step}]}]
    for _ in range(self.max_iterations):
        data = call_gemini(contents, TOOL_DECLARATIONS, "Be concise. Use tools.")
        parts = data["candidates"][0]["content"]["parts"]
        contents.append({"role": "model", "parts": parts})
        has_fc = False
        for p in parts:
            if "functionCall" in p:
                has_fc = True
                result = dispatch_tool(p["functionCall"]["name"], p["functionCall"].get("args", {}))
                contents.append({"role": "user", "parts": [
                    {"functionResponse": {"name": p["functionCall"]["name"], "response": {"result": result}}}
                ]})
        if not has_fc:
            return " ".join(p.get("text","") for p in parts if "text" in p)

HINT 5 — reflect():
    prompt = f"Rate this answer 1-10.\\nQ: {query}\\nA: {answer}\\nSCORE: <number>\\nREASON: <one line>"
    data = call_gemini([{"role": "user", "parts": [{"text": prompt}]}])
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    score = 5  # default
    for line in text.split("\\n"):
        if "SCORE:" in line.upper():
            try: score = int(line.split(":")[1].strip().split("/")[0].strip())
            except: pass
    return {"score": score, "passed": score >= self.reflection_threshold, "reason": text[:100]}
"""
