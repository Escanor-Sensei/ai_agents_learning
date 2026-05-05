"""
=============================================================================
DAY 3 - FILE 08: REFERENCE SOLUTION — Tool Use + Memory Agent
=============================================================================

⚠️  DO NOT READ THIS until you've attempted 07_task_build_memory.py yourself!
     Struggle is where learning happens.
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
        
        # Return all if no match
        all_items = [f"{k}: {d['value'] if isinstance(d, dict) else d}" for k, d in self.store.items()]
        return "No exact match. All memories:\n" + "\n".join(all_items)
    
    def list_all(self) -> str:
        if not self.store:
            return "No memories stored yet."
        items = [f"{k}: {d['value'] if isinstance(d, dict) else d}" for k, d in self.store.items()]
        return "All memories:\n" + "\n".join(items)


memory = MemoryStore()


# ---- TOOLS ----
def calculator(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"


TOOLS = {
    "calculator": calculator,
    "memory_save": None,  # Handled specially (needs key|value parsing)
    "memory_search": lambda q: memory.search(q),
    "memory_list": lambda _: memory.list_all(),
}

TOOL_DECLARATIONS = [
    {
        "name": "calculator",
        "description": "Calculate a math expression. Input: a Python expression like '2 + 3'.",
        "parameters": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"]
        }
    },
    {
        "name": "memory_save",
        "description": "Save an important fact to long-term memory. Use this when the user shares personal info, preferences, or asks you to remember something. Input: a key (short label) and value (the fact).",
        "parameters": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Short label like 'user_name', 'lucky_number'"},
                "value": {"type": "string", "description": "The fact to store"}
            },
            "required": ["key", "value"]
        }
    },
    {
        "name": "memory_search",
        "description": "Search long-term memory for previously stored facts. Use this when answering questions about the user or recalling past information.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Keyword to search for"}},
            "required": ["query"]
        }
    },
    {
        "name": "memory_list",
        "description": "List all stored memories. Use when user asks 'what do you know about me?'",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


# ---- LLM HELPERS ----
def call_llm_simple(prompt: str) -> str:
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    response = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, json=body)
    if response.status_code != 200:
        raise Exception(f"API error {response.status_code}: {response.text}")
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


def call_llm_with_tools(contents: list) -> dict:
    body = {
        "contents": contents,
        "tools": [{"functionDeclarations": TOOL_DECLARATIONS}],
        "systemInstruction": {
            "parts": [{"text": "You are a helpful assistant with memory. Use memory_save to store important user facts. Use memory_search before answering personal questions. Be concise."}]
        }
    }
    response = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, json=body)
    if response.status_code != 200:
        raise Exception(f"API error {response.status_code}: {response.text}")
    return response.json()


def dispatch_tool(tool_name: str, tool_args: dict) -> str:
    """Execute a tool call and return the result."""
    if tool_name == "calculator":
        return calculator(tool_args.get("expression", ""))
    elif tool_name == "memory_save":
        key = tool_args.get("key", "unknown")
        value = tool_args.get("value", "")
        return memory.save(key, value)
    elif tool_name == "memory_search":
        return memory.search(tool_args.get("query", ""))
    elif tool_name == "memory_list":
        return memory.list_all()
    else:
        return f"Unknown tool: {tool_name}"


# ---- REFLECTION ----
def reflect_on_answer(query: str, answer: str) -> tuple:
    eval_prompt = f"""Grade this answer 1-10.
Question: {query}
Answer: {answer}

Criteria: accuracy, completeness, clarity, specificity.
Format:
SCORE: <1-10>
CRITIQUE: <what needs improvement>"""
    
    response = call_llm_simple(eval_prompt)
    
    score = 5
    critique = response
    for line in response.split("\n"):
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
def run_agent_turn(contents: list, user_message: str, max_iterations: int = 8) -> tuple:
    """Run one turn with tool calling. Returns (response_text, updated_contents)."""
    
    contents.append({"role": "user", "parts": [{"text": user_message}]})
    
    for i in range(max_iterations):
        response_data = call_llm_with_tools(contents)
        candidate = response_data["candidates"][0]
        parts = candidate["content"]["parts"]
        contents.append({"role": "model", "parts": parts})
        
        has_function_call = False
        for part in parts:
            if "functionCall" in part:
                has_function_call = True
                func_call = part["functionCall"]
                tool_name = func_call["name"]
                tool_args = func_call.get("args", {})
                
                print(f"    [tool] {tool_name}({json.dumps(tool_args)[:60]})")
                result = dispatch_tool(tool_name, tool_args)
                print(f"    [result] {str(result)[:80]}")
                
                contents.append({
                    "role": "user",
                    "parts": [{"functionResponse": {"name": tool_name, "response": {"result": str(result)}}}]
                })
        
        if not has_function_call:
            text = " ".join(p.get("text", "") for p in parts if "text" in p)
            return text, contents
    
    return "Max iterations reached.", contents


def run_with_reflection(query: str, contents: list, max_attempts: int = 3, min_score: int = 7) -> tuple:
    """Run agent with reflection loop."""
    
    critique = ""
    for attempt in range(1, max_attempts + 1):
        msg = query
        if critique:
            msg = f"{query}\n\n[Previous feedback: {critique}. Please improve your answer.]"
        
        answer, contents = run_agent_turn(contents, msg)
        print(f"  [Attempt {attempt}] Answer: {answer[:100]}...")
        
        score, critique = reflect_on_answer(query, answer)
        print(f"  [Attempt {attempt}] Score: {score}/10")
        
        if score >= min_score:
            print(f"  ✓ Accepted (score {score} >= {min_score})")
            return answer, contents
    
    print(f"  ✗ Max attempts reached. Returning last answer.")
    return answer, contents


# ---- TEST ----
if __name__ == "__main__":
    # Clean slate
    memory.store = {}
    memory._save()
    
    print("=" * 60)
    print("CONVERSATION 1: Store facts")
    print("=" * 60)
    
    contents = []
    
    print("\nYou: My name is Nihal and my lucky number is 7. Remember this.")
    response, contents = run_agent_turn(contents, "My name is Nihal and my lucky number is 7. Remember this.")
    print(f"Bot: {response[:200]}")
    
    print("\nYou: What's my lucky number times 6?")
    response, contents = run_agent_turn(contents, "What's my lucky number times 6?")
    print(f"Bot: {response[:200]}")
    print(f"Expected: 42")
    
    print("\n\n" + "=" * 60)
    print("CONVERSATION 2: New session — long-term memory persists")
    print("=" * 60)
    
    contents = []  # Reset short-term memory
    
    print("\nYou: What do you remember about me?")
    response, contents = run_agent_turn(contents, "What do you remember about me?")
    print(f"Bot: {response[:200]}")
    print(f"Expected: Should find name=Nihal, lucky_number=7")
    
    print("\n\n" + "=" * 60)
    print("TEST: Reflection")
    print("=" * 60)
    
    contents = []
    answer, contents = run_with_reflection(
        "Explain what an AI agent is in exactly 3 bullet points",
        contents
    )
    print(f"\nFinal: {answer[:300]}")
    
    print("\n\n--- Stored memories ---")
    print(memory.list_all())
