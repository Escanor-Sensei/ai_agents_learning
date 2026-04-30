"""
=============================================================================
DAY 4 - FILE 09: REFERENCE SOLUTION — The Complete Smart Task Agent
=============================================================================

This is the complete solution for File 07's task.
Only look AFTER you've tried building it yourself!

This agent combines ALL 4 days:
- Day 1: LLM basics, prompts, agent loop
- Day 2: Tools, schemas, planning
- Day 3: Memory (short + long term), reflection
- Day 4: Error handling, evaluation-ready
=============================================================================
"""

import os
import json
import time
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


# =========================
# Memory Store
# =========================

class MemoryStore:
    def __init__(self, filepath: str = None):
        self.filepath = filepath or os.path.join(os.path.dirname(__file__), "agent_memory.json")
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                self.memories = json.load(f)
        else:
            self.memories = {}
    
    def _save_file(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.memories, f, indent=2)
    
    def save(self, key: str, value: str, category: str = "general") -> str:
        self.memories[key] = {
            "value": value,
            "category": category,
            "timestamp": datetime.now().isoformat(),
        }
        self._save_file()
        return f"Saved: '{key}'"
    
    def search(self, query: str) -> list:
        query_words = query.lower().split()
        results = []
        for key, data in self.memories.items():
            text = f"{key} {data['value']}".lower()
            score = sum(1 for w in query_words if w in text)
            if score > 0:
                results.append({"key": key, "value": data["value"], "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:5]
    
    def list_all(self) -> list:
        return list(self.memories.keys())


# =========================
# Tools
# =========================

def calculator(expression: str) -> str:
    try:
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return "Error: Invalid characters. Math only."
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

def search_web(query: str) -> str:
    SEARCH_DB = {
        "python": "Python is a high-level programming language created by Guido van Rossum in 1991. Latest version: 3.12.",
        "machine learning": "Machine learning is a subset of AI. Systems learn patterns from data without explicit programming.",
        "langchain": "LangChain is a framework for building LLM-powered applications with chains, agents, and tools.",
        "react pattern": "ReAct (Reasoning + Acting) is an agent pattern where the LLM thinks step-by-step and uses tools.",
    }
    for key, val in SEARCH_DB.items():
        if key in query.lower():
            return val
    return f"No specific results for: {query}. Try a more specific search."

def read_file_tool(file_path: str) -> str:
    try:
        safe_name = os.path.basename(file_path)
        search_dirs = [
            os.path.dirname(__file__),
            os.path.join(os.path.dirname(__file__), "..", "day2"),
        ]
        for d in search_dirs:
            full = os.path.join(d, safe_name)
            if os.path.exists(full):
                with open(full, "r", encoding="utf-8") as f:
                    return f.read()[:2000]
        return f"Error: File '{safe_name}' not found."
    except Exception as e:
        return f"Error: {e}"

def get_current_time(fmt: str = "full") -> str:
    now = datetime.now()
    if fmt == "date": return now.strftime("%Y-%m-%d")
    if fmt == "time": return now.strftime("%H:%M:%S")
    return now.strftime("%Y-%m-%d %H:%M:%S")

def get_word_length(word: str) -> str:
    return str(len(word))

# Global memory store for tool access
_memory_store = MemoryStore()

TOOL_FUNCTIONS = {
    "calculator": lambda args: calculator(args.get("expression", "")),
    "search_web": lambda args: search_web(args.get("query", "")),
    "read_file": lambda args: read_file_tool(args.get("file_path", "")),
    "get_current_time": lambda args: get_current_time(args.get("format", "full")),
    "get_word_length": lambda args: get_word_length(args.get("word", "")),
    "memory_save": lambda args: _memory_store.save(args.get("key", ""), args.get("value", ""), args.get("category", "general")),
    "memory_search": lambda args: json.dumps(_memory_store.search(args.get("query", ""))),
    "memory_list": lambda args: json.dumps(_memory_store.list_all()),
}

TOOL_DECLARATIONS = [
    {"name": "calculator", "description": "Calculate a math expression. Returns the numeric result.",
     "parameters": {"type": "object", "properties": {"expression": {"type": "string", "description": "Math expression like '2+3*4'"}}, "required": ["expression"]}},
    {"name": "search_web", "description": "Search the web for information about a topic.",
     "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "Search query"}}, "required": ["query"]}},
    {"name": "read_file", "description": "Read a text file and return its contents.",
     "parameters": {"type": "object", "properties": {"file_path": {"type": "string", "description": "Filename to read"}}, "required": ["file_path"]}},
    {"name": "get_current_time", "description": "Get current date and/or time.",
     "parameters": {"type": "object", "properties": {"format": {"type": "string", "description": "full, date, or time"}}, "required": ["format"]}},
    {"name": "get_word_length", "description": "Count the number of characters in a word.",
     "parameters": {"type": "object", "properties": {"word": {"type": "string", "description": "Word to count"}}, "required": ["word"]}},
    {"name": "memory_save", "description": "Save a fact to long-term memory for future reference.",
     "parameters": {"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}, "category": {"type": "string"}}, "required": ["key", "value"]}},
    {"name": "memory_search", "description": "Search long-term memory for relevant past information.",
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "memory_list", "description": "List all keys stored in long-term memory.",
     "parameters": {"type": "object", "properties": {}, "required": []}},
]


# =========================
# Core Functions
# =========================

def call_gemini(contents: list, tools: list = None, system: str = None) -> dict:
    body = {"contents": contents}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    if tools:
        body["tools"] = [{"functionDeclarations": tools}]
    
    for attempt in range(4):
        try:
            resp = requests.post(
                GEMINI_URL,
                headers={"Content-Type": "application/json"},
                json=body,
                timeout=30,
            )
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 429:
                wait = (2 ** attempt) + 1
                print(f"    [rate-limit] Waiting {wait}s...")
                time.sleep(wait)
                continue
            else:
                raise Exception(f"API error {resp.status_code}: {resp.text[:200]}")
        except requests.exceptions.Timeout:
            if attempt < 3:
                continue
            raise
    raise Exception("API failed after retries")


def dispatch_tool(name: str, args: dict) -> str:
    if name not in TOOL_FUNCTIONS:
        return f"Error: Unknown tool '{name}'"
    try:
        return str(TOOL_FUNCTIONS[name](args))
    except Exception as e:
        return f"Error in {name}: {e}"


# =========================
# The Complete Smart Task Agent
# =========================

class SmartTaskAgent:
    def __init__(self):
        self.memory = _memory_store
        self.conversation = []
        self.max_iterations = 10
        self.reflection_threshold = 7
    
    def plan(self, query: str) -> list:
        """Generate a step-by-step plan."""
        prompt = (
            f"Break this task into 1-4 short, actionable steps. "
            f"Return ONLY a JSON array of step strings. No explanation.\n"
            f"Task: {query}"
        )
        try:
            data = call_gemini([{"role": "user", "parts": [{"text": prompt}]}])
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            text = text.strip().strip("```json").strip("```").strip()
            steps = json.loads(text)
            if isinstance(steps, list):
                return steps
        except Exception as e:
            print(f"    [plan] Failed to parse plan: {e}")
        
        # Fallback: treat the whole query as one step
        return [query]
    
    def execute_step(self, step: str) -> str:
        """Execute a single step using the agent loop."""
        contents = [{"role": "user", "parts": [{"text": step}]}]
        recent_calls = []
        
        for i in range(self.max_iterations):
            data = call_gemini(contents, TOOL_DECLARATIONS, "Be concise. Use tools when needed.")
            parts = data["candidates"][0]["content"]["parts"]
            contents.append({"role": "model", "parts": parts})
            
            has_fc = False
            for p in parts:
                if "functionCall" in p:
                    has_fc = True
                    fc = p["functionCall"]
                    name = fc["name"]
                    args = fc.get("args", {})
                    
                    # Stuck detection
                    sig = f"{name}({json.dumps(args, sort_keys=True)})"
                    recent_calls.append(sig)
                    if len(recent_calls) >= 3 and len(set(recent_calls[-3:])) == 1:
                        return f"Got stuck calling {name} repeatedly."
                    
                    result = dispatch_tool(name, args)
                    contents.append({"role": "user", "parts": [
                        {"functionResponse": {"name": name, "response": {"result": result}}}
                    ]})
            
            if not has_fc:
                return " ".join(p.get("text", "") for p in parts if "text" in p)
        
        return "Could not complete step within iteration limit."
    
    def reflect(self, query: str, answer: str) -> dict:
        """Evaluate answer quality using LLM."""
        prompt = (
            f"Rate this answer on a scale of 1-10 for correctness and helpfulness.\n"
            f"Question: {query}\n"
            f"Answer: {answer}\n\n"
            f"Respond with:\nSCORE: <number>\nREASON: <one sentence>"
        )
        try:
            data = call_gemini([{"role": "user", "parts": [{"text": prompt}]}])
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            
            score = 7  # default
            reason = text[:100]
            for line in text.split("\n"):
                l = line.strip()
                if l.upper().startswith("SCORE:"):
                    try:
                        score = int(l.split(":")[1].strip().split("/")[0].strip())
                    except:
                        pass
                elif l.upper().startswith("REASON:"):
                    reason = l.split(":", 1)[1].strip()[:100]
            
            return {"score": score, "passed": score >= self.reflection_threshold, "reason": reason}
        except Exception as e:
            return {"score": 5, "passed": False, "reason": f"Reflection failed: {e}"}
    
    def remember(self, query: str, answer: str):
        """Save query+answer to long-term memory."""
        if "error" not in answer.lower() and len(answer) > 5:
            key = query[:50].strip()
            self.memory.save(key, answer[:500], category="agent_answer")
    
    def check_memory(self, query: str) -> str:
        """Check if similar query was answered before."""
        results = self.memory.search(query)
        if results and results[0]["score"] >= 2:
            cached = results[0]
            return f"[From memory] {cached['value']}"
        return None
    
    def run(self, query: str) -> str:
        """Main pipeline: check memory → plan → execute → reflect → remember."""
        print(f"\n  [agent] Query: {query}")
        
        # 1. Check memory cache
        cached = self.check_memory(query)
        if cached:
            print(f"  [memory] Cache hit!")
            return cached
        
        # 2. Plan
        print(f"  [plan] Generating plan...")
        steps = self.plan(query)
        print(f"  [plan] Steps: {steps}")
        
        # 3. Execute
        step_results = []
        for i, step in enumerate(steps):
            print(f"  [execute] Step {i+1}: {step[:60]}")
            result = self.execute_step(step)
            step_results.append(result)
            print(f"  [result] {result[:80]}")
        
        # 4. Combine results
        if len(step_results) == 1:
            answer = step_results[0]
        else:
            # Ask LLM to combine multiple results
            combine_prompt = (
                f"Original question: {query}\n\n"
                f"Step results:\n" +
                "\n".join(f"- {r}" for r in step_results) +
                "\n\nCombine these into a clear, concise final answer."
            )
            data = call_gemini([{"role": "user", "parts": [{"text": combine_prompt}]}])
            answer = data["candidates"][0]["content"]["parts"][0]["text"]
        
        # 5. Reflect
        print(f"  [reflect] Evaluating answer...")
        reflection = self.reflect(query, answer)
        print(f"  [reflect] Score: {reflection['score']}/10 — {reflection['reason']}")
        
        if not reflection["passed"]:
            print(f"  [reflect] Score below threshold. Improving...")
            improve_prompt = (
                f"The answer to '{query}' was: {answer}\n"
                f"Issue: {reflection['reason']}\n"
                f"Please provide an improved, correct answer."
            )
            answer = self.execute_step(improve_prompt)
            print(f"  [improved] {answer[:80]}")
        
        # 6. Remember
        self.remember(query, answer)
        print(f"  [memory] Saved to memory")
        
        return answer


# =========================
# Test the complete agent
# =========================
if __name__ == "__main__":
    agent = SmartTaskAgent()
    
    print("=" * 70)
    print("SMART TASK AGENT — Complete Reference Solution")
    print("=" * 70)
    
    test_queries = [
        "What is 42 * 17?",
        "Search for information about Python and tell me who created it",
        "What time is it right now?",
        "What is 42 * 17?",  # Should hit memory cache!
    ]
    
    for q in test_queries:
        print(f"\n{'='*60}")
        result = agent.run(q)
        print(f"\n  FINAL ANSWER: {result[:200]}")
    
    # Show memory state
    print(f"\n\n{'='*60}")
    print("MEMORY STATE:")
    for key in agent.memory.list_all():
        mem = agent.memory.memories[key]
        print(f"  [{mem['category']}] {key}: {mem['value'][:60]}")
    
    print("""
    ARCHITECTURE SUMMARY:
    
    ┌──────────────────────────────────────────────────────────┐
    │                  SmartTaskAgent.run()                    │
    │                                                         │
    │  1. check_memory() ─→ cache hit? return early           │
    │          │                                               │
    │          ↓                                               │
    │  2. plan() ─→ break query into steps                    │
    │          │                                               │
    │          ↓                                               │
    │  3. execute_step() ─→ agent loop with tools             │
    │     ├─ call_gemini() with TOOL_DECLARATIONS             │
    │     ├─ dispatch_tool() with error handling              │
    │     └─ stuck detection (repeated calls)                 │
    │          │                                               │
    │          ↓                                               │
    │  4. reflect() ─→ LLM evaluates answer (1-10)           │
    │     └─ if score < 7: improve and retry once             │
    │          │                                               │
    │          ↓                                               │
    │  5. remember() ─→ save to long-term memory              │
    │                                                         │
    │  Components: MemoryStore, 8 tools, Gemini API           │
    │  Lines of code: ~250 (zero frameworks)                  │
    └──────────────────────────────────────────────────────────┘
    """)
