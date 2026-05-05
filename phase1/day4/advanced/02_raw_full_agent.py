"""
=============================================================================
DAY 4 - FILE 02: THE COMPLETE AGENT — RAW (Zero Frameworks)
=============================================================================

CONCEPT (5 lines):
- File 01 used LangChain/LangGraph. This file does the SAME thing with zero imports.
- Only dependencies: requests, json, os — that's it.
- Every piece is visible: tool registry, API calls, agent loop, memory, reflection.
- Compare line counts: framework ~100 LOC vs raw ~300 LOC.
- The framework saves effort, but you UNDERSTAND what it does because you built it raw.

THIS IS THE MOST IMPORTANT FILE OF THE ENTIRE 4-DAY COURSE.
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

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "agent_memory_raw.json")


# =============================================================================
# COMPONENT 1: TOOL REGISTRY
# =============================================================================

def calculator(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

def get_word_length(word: str) -> str:
    return str(len(word))

def search_web(query: str) -> str:
    SEARCH_DB = {
        "python": "Python is a high-level programming language created by Guido van Rossum in 1991.",
        "langchain": "LangChain is a framework for building LLM applications.",
        "machine learning": "Machine learning is a subset of AI. Types: supervised, unsupervised, reinforcement.",
        "react pattern": "ReAct = Reasoning + Acting. An agent pattern from Yao et al. 2022.",
        "weather": "Current weather: 72°F, partly cloudy.",
        "population": "World population: approximately 8.1 billion.",
    }
    for key, val in SEARCH_DB.items():
        if key in query.lower():
            return val
    return f"No results for: {query}"

def read_file_tool(file_path: str) -> str:
    try:
        safe_path = os.path.basename(file_path)
        for dir_path in [os.path.dirname(__file__), os.path.join(os.path.dirname(__file__), "..", "day2")]:
            full = os.path.join(dir_path, safe_path)
            if os.path.exists(full):
                with open(full, "r", encoding="utf-8") as f:
                    return f.read()[:2000]
        return f"Error: File '{safe_path}' not found."
    except Exception as e:
        return f"Error: {e}"

def get_current_time(format_type: str = "full") -> str:
    now = datetime.now()
    if format_type == "date": return now.strftime("%Y-%m-%d")
    if format_type == "time": return now.strftime("%H:%M:%S")
    return now.strftime("%Y-%m-%d %H:%M:%S")


# =============================================================================
# COMPONENT 2: LONG-TERM MEMORY
# =============================================================================

class MemoryStore:
    def __init__(self):
        self.file_path = MEMORY_FILE
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
        self.store[key] = {"value": value, "saved_at": datetime.now().isoformat()}
        self._save()
        return f"Saved: {key} = {value}"
    
    def search(self, query: str) -> str:
        if not self.store:
            return "No memories stored."
        q = query.lower()
        matches = [f"{k}: {d['value']}" for k, d in self.store.items()
                   if q in k.lower() or q in d.get("value", "").lower()]
        if matches:
            return "Found:\n" + "\n".join(matches)
        return "All memories:\n" + "\n".join(f"{k}: {d['value']}" for k, d in self.store.items())

memory = MemoryStore()


# =============================================================================
# COMPONENT 3: TOOL DISPATCH TABLE
# =============================================================================

def dispatch_tool(name: str, args: dict) -> str:
    """Route function calls to the right tool."""
    if name == "calculator":
        return calculator(args.get("expression", ""))
    elif name == "get_word_length":
        return get_word_length(args.get("word", ""))
    elif name == "search_web":
        return search_web(args.get("query", ""))
    elif name == "read_file":
        return read_file_tool(args.get("file_path", ""))
    elif name == "get_current_time":
        return get_current_time(args.get("format", "full"))
    elif name == "memory_save":
        return memory.save(args.get("key", ""), args.get("value", ""))
    elif name == "memory_search":
        return memory.search(args.get("query", ""))
    else:
        return f"Unknown tool: {name}"


TOOL_DECLARATIONS = [
    {"name": "calculator", "description": "Calculate a math expression. Input: Python expression like '2+3*4'.",
     "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}},
    {"name": "get_word_length", "description": "Count characters in a word/phrase.",
     "parameters": {"type": "object", "properties": {"word": {"type": "string"}}, "required": ["word"]}},
    {"name": "search_web", "description": "Search web for information. Input: search query.",
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "read_file", "description": "Read a text file. Input: filename like 'notes.txt'.",
     "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}},
    {"name": "get_current_time", "description": "Get current date/time. Input: 'full', 'date', or 'time'.",
     "parameters": {"type": "object", "properties": {"format": {"type": "string"}}, "required": ["format"]}},
    {"name": "memory_save", "description": "Save a fact to persistent memory. Use when user shares important info.",
     "parameters": {"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}}, "required": ["key", "value"]}},
    {"name": "memory_search", "description": "Search persistent memory for stored facts. Use before answering personal questions.",
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
]


# =============================================================================
# COMPONENT 4: API CALL
# =============================================================================

def call_gemini(contents: list) -> dict:
    body = {
        "contents": contents,
        "tools": [{"functionDeclarations": TOOL_DECLARATIONS}],
        "systemInstruction": {
            "parts": [{"text": "You are a helpful Smart Task Agent. Use tools when needed. Save important user facts to memory. Search memory before answering personal questions. Be concise and accurate."}]
        }
    }
    response = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, json=body)
    if response.status_code != 200:
        raise Exception(f"API error {response.status_code}: {response.text}")
    return response.json()

def call_llm_simple(prompt: str) -> str:
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    response = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, json=body)
    if response.status_code != 200:
        raise Exception(f"API error {response.status_code}: {response.text}")
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


# =============================================================================
# COMPONENT 5: AGENT LOOP
# =============================================================================

def agent_loop(contents: list, max_iterations: int = 10) -> tuple:
    """
    THE CORE LOOP: call LLM → handle tools → repeat until text response.
    Returns (answer_text, updated_contents).
    """
    for i in range(max_iterations):
        response_data = call_gemini(contents)
        candidate = response_data["candidates"][0]
        parts = candidate["content"]["parts"]
        contents.append({"role": "model", "parts": parts})
        
        has_func_call = False
        for part in parts:
            if "functionCall" in part:
                has_func_call = True
                fc = part["functionCall"]
                tool_name = fc["name"]
                tool_args = fc.get("args", {})
                
                result = dispatch_tool(tool_name, tool_args)
                
                contents.append({
                    "role": "user",
                    "parts": [{"functionResponse": {"name": tool_name, "response": {"result": str(result)}}}]
                })
        
        if not has_func_call:
            text = " ".join(p.get("text", "") for p in parts if "text" in p)
            return text, contents
    
    return "Max iterations reached.", contents


# =============================================================================
# COMPONENT 6: REFLECTION
# =============================================================================

def evaluate_answer(query: str, answer: str) -> tuple:
    eval_prompt = f"""Grade 1-10. Be strict.
Q: {query}
A: {answer}
Format:
SCORE: <1-10>
CRITIQUE: <feedback>"""
    
    text = call_llm_simple(eval_prompt)
    score = 5
    critique = text
    for line in text.split("\n"):
        l = line.strip()
        if l.upper().startswith("SCORE:"):
            try: score = max(1, min(10, int(l.split(":")[1].strip().split("/")[0].strip())))
            except: score = 5
        elif l.upper().startswith("CRITIQUE:"):
            critique = l.split(":", 1)[1].strip()
    return score, critique


# =============================================================================
# COMPONENT 7: THE COMPLETE AGENT
# =============================================================================

class SmartTaskAgentRaw:
    """
    Complete Smart Task Agent — raw Python, zero frameworks.
    
    COMPONENTS:
    1. Tool Registry + Dispatch
    2. Long-term Memory (JSON file)
    3. Short-term Memory (contents list per session)
    4. Agent Loop (call LLM → handle tools → repeat)
    5. Reflection (evaluate → retry if poor)
    """
    
    def __init__(self):
        self.sessions = {}  # session_id → contents list (short-term memory)
    
    def new_session(self) -> str:
        session_id = f"session-{len(self.sessions) + 1}"
        self.sessions[session_id] = []
        return session_id
    
    def chat(self, session_id: str, message: str, reflect: bool = False) -> str:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        contents = self.sessions[session_id]
        
        # Add user message
        contents.append({"role": "user", "parts": [{"text": message}]})
        
        # Run agent loop
        answer, contents = agent_loop(contents)
        self.sessions[session_id] = contents
        
        # Optional reflection
        if reflect:
            score, critique = evaluate_answer(message, answer)
            if score < 7:
                # Retry with critique
                retry_msg = f"{message}\n\n[Feedback: {critique}. Improve your answer.]"
                contents.append({"role": "user", "parts": [{"text": retry_msg}]})
                answer, contents = agent_loop(contents)
                self.sessions[session_id] = contents
        
        return answer


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    agent = SmartTaskAgentRaw()
    
    # Session 1
    print("=" * 60)
    print("SESSION 1: Full capabilities (RAW agent)")
    print("=" * 60)
    
    sid = agent.new_session()
    
    queries = [
        "My name is Nihal. I love AI agents. Remember this.",
        "What is 42 * 17?",
        "Search for info about Python",
        "Read notes.txt and tell me the main summary",
        "What time is it?",
        "What's my name? Check your memory.",
    ]
    
    for q in queries:
        print(f"\nYou: {q}")
        answer = agent.chat(sid, q)
        print(f"Bot: {answer[:200]}")
    
    # Session 2: Long-term memory persists
    print("\n\n" + "=" * 60)
    print("SESSION 2: New session — long-term memory persists")
    print("=" * 60)
    
    sid2 = agent.new_session()
    print("\nYou: What do you remember about me?")
    answer = agent.chat(sid2, "Search your memory — what do you know about me?")
    print(f"Bot: {answer[:200]}")
    
    # Line count comparison
    print("\n\n" + "=" * 60)
    print("FRAMEWORK vs RAW: Line Count Comparison")
    print("=" * 60)
    print("""
    ┌──────────────────┬─────────────────┬─────────────────┐
    │ Component        │ Framework (01)  │ Raw (this file) │
    ├──────────────────┼─────────────────┼─────────────────┤
    │ Tool definitions │ ~40 lines       │ ~50 lines       │
    │ Tool schemas     │ 0 (auto-gen)    │ ~30 lines       │
    │ Memory store     │ ~20 lines       │ ~40 lines       │
    │ Agent loop       │ 1 line (!)      │ ~25 lines       │
    │ Reflection       │ ~15 lines       │ ~20 lines       │
    │ Glue code        │ ~30 lines       │ ~40 lines       │
    ├──────────────────┼─────────────────┼─────────────────┤
    │ TOTAL            │ ~105 lines      │ ~205 lines      │
    └──────────────────┴─────────────────┴─────────────────┘
    
    Framework saves ~100 lines. But now you KNOW what those 100 lines do.
    
    When to use framework:  Production code, rapid prototyping, team projects
    When to use raw:        Learning, debugging, custom behavior, edge cases
    """)

    # KEY OBSERVATION:
    # - Same functionality, no framework imports (just requests, json, os)
    # - You can see EVERY piece: tool dispatch, API call, agent loop, memory, reflection
    # - The framework is not magic — it's just well-organized Python code
    # - Understanding the raw version makes you a MUCH better framework user
    #
    # → File 03: Add structured logging to trace every decision
