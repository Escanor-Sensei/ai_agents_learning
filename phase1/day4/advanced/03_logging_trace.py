"""
=============================================================================
DAY 4 - FILE 03: STRUCTURED LOGGING & TRACING
=============================================================================

CONCEPT (5 lines):
- Production agents need OBSERVABILITY — see what happened and why.
- Tracing = recording every step: tool selection, inputs, outputs, duration.
- This is what LangSmith, LangFuse, and OpenTelemetry do for agents.
- We build our own: a trace is a list of {step, action, input, output, duration}.
- Print a readable summary after each run — instant debugging.

ANALOGY FOR .NET DEVS:
- Like Application Insights / Serilog structured logging.
- Each agent step = a trace span with parent-child relationships.
- The trace summary = the "end-to-end request trace" in your APM tool.
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
# STEP 1: The Trace class
# =========================

class AgentTrace:
    """Records every step of agent execution for debugging."""
    
    def __init__(self, query: str):
        self.query = query
        self.steps = []
        self.start_time = time.time()
        self.total_tokens_estimate = 0
    
    def log_step(self, action: str, input_data: str, output_data: str, duration: float, metadata: dict = None):
        step = {
            "step": len(self.steps) + 1,
            "action": action,
            "input": str(input_data)[:200],
            "output": str(output_data)[:200],
            "duration_ms": round(duration * 1000, 1),
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.steps.append(step)
    
    def print_summary(self):
        """Print a readable trace summary."""
        total_time = time.time() - self.start_time
        
        print(f"\n{'='*60}")
        print(f"TRACE SUMMARY")
        print(f"{'='*60}")
        print(f"Query: {self.query[:80]}")
        print(f"Total steps: {len(self.steps)}")
        print(f"Total time: {total_time:.2f}s")
        print(f"{'─'*60}")
        
        for step in self.steps:
            icon = "🔧" if step["action"] == "tool_call" else "🤖" if step["action"] == "llm_call" else "📝"
            print(f"  {icon} Step {step['step']}: {step['action']}")
            print(f"     Input:  {step['input'][:80]}")
            print(f"     Output: {step['output'][:80]}")
            print(f"     Time:   {step['duration_ms']}ms")
            if step["metadata"]:
                for k, v in step["metadata"].items():
                    print(f"     {k}: {v}")
            print()
        
        print(f"{'─'*60}")
        
        # Summary stats
        llm_steps = [s for s in self.steps if s["action"] == "llm_call"]
        tool_steps = [s for s in self.steps if s["action"] == "tool_call"]
        
        print(f"  LLM calls: {len(llm_steps)} ({sum(s['duration_ms'] for s in llm_steps):.0f}ms)")
        print(f"  Tool calls: {len(tool_steps)} ({sum(s['duration_ms'] for s in tool_steps):.0f}ms)")
        print(f"  Total: {total_time*1000:.0f}ms")
        print(f"{'='*60}")
    
    def to_json(self) -> str:
        """Export trace as JSON for external analysis."""
        return json.dumps({
            "query": self.query,
            "total_time_ms": round((time.time() - self.start_time) * 1000, 1),
            "steps": self.steps
        }, indent=2)


# =========================
# STEP 2: Tools
# =========================

def calculator(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

def search_web(query: str) -> str:
    SEARCH_DB = {
        "python": "Python is a high-level programming language.",
        "langchain": "LangChain is a framework for LLM apps.",
        "machine learning": "ML is a subset of AI where systems learn from data.",
    }
    for key, val in SEARCH_DB.items():
        if key in query.lower():
            return val
    return f"No results for: {query}"

def read_file_tool(file_path: str) -> str:
    try:
        safe_path = os.path.basename(file_path)
        for d in [os.path.dirname(__file__), os.path.join(os.path.dirname(__file__), "..", "day2")]:
            full = os.path.join(d, safe_path)
            if os.path.exists(full):
                with open(full, "r", encoding="utf-8") as f:
                    return f.read()[:2000]
        return f"Error: File '{safe_path}' not found."
    except Exception as e:
        return f"Error: {e}"

def get_current_time(fmt: str = "full") -> str:
    now = datetime.now()
    if fmt == "date": return now.strftime("%Y-%m-%d")
    if fmt == "time": return now.strftime("%H:%M:%S")
    return now.strftime("%Y-%m-%d %H:%M:%S")


TOOL_FUNCTIONS = {
    "calculator": lambda args: calculator(args.get("expression", "")),
    "search_web": lambda args: search_web(args.get("query", "")),
    "read_file": lambda args: read_file_tool(args.get("file_path", "")),
    "get_current_time": lambda args: get_current_time(args.get("format", "full")),
}

TOOL_DECLARATIONS = [
    {"name": "calculator", "description": "Calculate math expressions.",
     "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}},
    {"name": "search_web", "description": "Search web for information.",
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "read_file", "description": "Read a text file.",
     "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}},
    {"name": "get_current_time", "description": "Get current date/time.",
     "parameters": {"type": "object", "properties": {"format": {"type": "string"}}, "required": ["format"]}},
]


# =========================
# STEP 3: Traced agent loop
# =========================

def call_gemini(contents: list) -> dict:
    body = {
        "contents": contents,
        "tools": [{"functionDeclarations": TOOL_DECLARATIONS}],
        "systemInstruction": {"parts": [{"text": "You are a helpful assistant. Use tools when needed. Be concise."}]}
    }
    response = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, json=body)
    if response.status_code != 200:
        raise Exception(f"API error {response.status_code}: {response.text}")
    return response.json()


def run_traced_agent(query: str, max_iterations: int = 10) -> tuple:
    """Run agent with full tracing. Returns (answer, trace)."""
    
    trace = AgentTrace(query)
    contents = [{"role": "user", "parts": [{"text": query}]}]
    
    for i in range(max_iterations):
        # LLM call
        t0 = time.time()
        response_data = call_gemini(contents)
        llm_duration = time.time() - t0
        
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
                
                trace.log_step("llm_call", query, f"→ {tool_name}({json.dumps(tool_args)[:60]})", llm_duration,
                             {"decision": "use_tool", "tool": tool_name})
                
                # Tool call
                t1 = time.time()
                if tool_name in TOOL_FUNCTIONS:
                    result = TOOL_FUNCTIONS[tool_name](tool_args)
                else:
                    result = f"Unknown tool: {tool_name}"
                tool_duration = time.time() - t1
                
                trace.log_step("tool_call", f"{tool_name}({json.dumps(tool_args)[:60]})", str(result)[:100], tool_duration,
                             {"tool": tool_name})
                
                contents.append({
                    "role": "user",
                    "parts": [{"functionResponse": {"name": tool_name, "response": {"result": str(result)}}}]
                })
            
            elif "text" in part:
                if not has_func_call:
                    trace.log_step("llm_call", query, part["text"][:100], llm_duration,
                                 {"decision": "final_answer"})
        
        if not has_func_call:
            text = " ".join(p.get("text", "") for p in parts if "text" in p)
            return text, trace
    
    return "Max iterations.", trace


# =========================
# STEP 4: Test with tracing
# =========================
if __name__ == "__main__":
    # Test 1: Simple
    print("TEST 1: Math query")
    answer1, trace1 = run_traced_agent("What is 42 * 17?")
    print(f"Answer: {answer1[:100]}")
    trace1.print_summary()
    
    # Test 2: Multi-tool
    print("\n\nTEST 2: Multi-step query")
    answer2, trace2 = run_traced_agent(
        "Search for info about Python and tell me how many characters are in the word 'Python'"
    )
    print(f"Answer: {answer2[:100]}")
    trace2.print_summary()
    
    # Test 3: File + calculation
    print("\n\nTEST 3: File read + calculation")
    answer3, trace3 = run_traced_agent("Read notes.txt and tell me how many known issues there are")
    print(f"Answer: {answer3[:100]}")
    trace3.print_summary()
    
    # Export one trace as JSON
    print("\n\nTRACE AS JSON (for external tools):")
    print(trace2.to_json())
    
    print("""
    THIS IS WHAT LANGSMITH / LANGFUSE DO:
    
    ┌──────────────┐
    │ Your Agent   │──→ trace.log_step() at every decision point
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Trace Store  │──→ JSON file, database, or cloud service
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Dashboard    │──→ Visualize traces, find bottlenecks, debug failures
    └──────────────┘
    
    The difference: LangSmith has a nice UI and auto-instruments LangChain.
    We built the same trace data structure from scratch.
    """)

    # KEY OBSERVATION:
    # - Tracing = recording {action, input, output, duration} for every step
    # - This is ESSENTIAL for debugging ("why did the agent pick that tool?")
    # - Also essential for optimization ("which step is slowest?")
    # - Production tools (LangSmith, LangFuse) do this automatically with a nice UI
    # - But the underlying data is exactly what we built here
    #
    # → File 04: Error handling — what happens when things go wrong?
