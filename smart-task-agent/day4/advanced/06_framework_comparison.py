"""
=============================================================================
DAY 4 - FILE 06: FRAMEWORK vs RAW — Final Comparison
=============================================================================

CONCEPT (5 lines):
- You've now built the same agent TWO ways: framework (LangChain) and raw (requests).
- This file runs identical queries through both and compares results.
- Tradeoffs: framework saves code but hides details. Raw is verbose but transparent.
- Neither is "better" — the right choice depends on the situation.
- Now you can make an INFORMED choice because you understand both.

THIS FILE IS THE CULMINATION OF 4 DAYS OF LEARNING.
=============================================================================
"""

import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

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
# AGENT A: Framework (LangChain/LangGraph)
# =========================

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))

@tool
def fw_calculator(expression: str) -> str:
    """Calculate a math expression. Input: Python expression like '2 + 3 * 4'."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

@tool
def fw_search(query: str) -> str:
    """Search the web for information. Input: search query."""
    SEARCH_DB = {
        "python": "Python is a high-level programming language created by Guido van Rossum.",
        "langchain": "LangChain is a framework for building LLM applications.",
        "machine learning": "ML is a subset of AI where systems learn from data.",
    }
    for key, val in SEARCH_DB.items():
        if key in query.lower():
            return val
    return f"No results for: {query}"

@tool
def fw_read_file(file_path: str) -> str:
    """Read a text file. Input: filename."""
    try:
        safe = os.path.basename(file_path)
        for d in [os.path.dirname(__file__), os.path.join(os.path.dirname(__file__), "..", "day2")]:
            full = os.path.join(d, safe)
            if os.path.exists(full):
                with open(full, "r", encoding="utf-8") as f:
                    return f.read()[:2000]
        return f"Error: File '{safe}' not found."
    except Exception as e:
        return f"Error: {e}"

framework_agent = create_react_agent(model=llm, tools=[fw_calculator, fw_search, fw_read_file])


def run_framework_agent(query: str) -> tuple:
    """Run framework agent. Returns (answer, duration)."""
    t0 = time.time()
    result = framework_agent.invoke({"messages": [("human", query)]})
    duration = time.time() - t0
    answer = str(result["messages"][-1].content)
    return answer, duration


# =========================
# AGENT B: Raw (requests + Gemini API)
# =========================

def raw_calculator(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

def raw_search(query: str) -> str:
    SEARCH_DB = {
        "python": "Python is a high-level programming language created by Guido van Rossum.",
        "langchain": "LangChain is a framework for building LLM applications.",
        "machine learning": "ML is a subset of AI where systems learn from data.",
    }
    for key, val in SEARCH_DB.items():
        if key in query.lower():
            return val
    return f"No results for: {query}"

def raw_read_file(file_path: str) -> str:
    try:
        safe = os.path.basename(file_path)
        for d in [os.path.dirname(__file__), os.path.join(os.path.dirname(__file__), "..", "day2")]:
            full = os.path.join(d, safe)
            if os.path.exists(full):
                with open(full, "r", encoding="utf-8") as f:
                    return f.read()[:2000]
        return f"Error: File '{safe}' not found."
    except Exception as e:
        return f"Error: {e}"

RAW_TOOLS = {"calculator": raw_calculator, "search_web": raw_search, "read_file": raw_read_file}

RAW_DECLARATIONS = [
    {"name": "calculator", "description": "Calculate math expressions.",
     "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}},
    {"name": "search_web", "description": "Search web for information.",
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "read_file", "description": "Read a text file.",
     "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}},
]


def run_raw_agent(query: str, max_iter: int = 10) -> tuple:
    """Run raw agent. Returns (answer, duration)."""
    t0 = time.time()
    contents = [{"role": "user", "parts": [{"text": query}]}]
    
    for _ in range(max_iter):
        body = {
            "contents": contents,
            "tools": [{"functionDeclarations": RAW_DECLARATIONS}],
            "systemInstruction": {"parts": [{"text": "Be concise. Use tools when needed."}]}
        }
        resp = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, json=body)
        if resp.status_code != 200:
            return f"Error: {resp.status_code}", time.time() - t0
        
        parts = resp.json()["candidates"][0]["content"]["parts"]
        contents.append({"role": "model", "parts": parts})
        
        has_fc = False
        for p in parts:
            if "functionCall" in p:
                has_fc = True
                fc = p["functionCall"]
                name = fc["name"]
                args = fc.get("args", {})
                arg_val = list(args.values())[0] if args else ""
                
                result = RAW_TOOLS.get(name, lambda x: f"Unknown: {name}")(arg_val)
                contents.append({"role": "user", "parts": [
                    {"functionResponse": {"name": name, "response": {"result": str(result)}}}
                ]})
        
        if not has_fc:
            text = " ".join(p.get("text", "") for p in parts if "text" in p)
            return text, time.time() - t0
    
    return "Max iterations.", time.time() - t0


# =========================
# STEP 3: Head-to-head comparison
# =========================

TEST_QUERIES = [
    "What is 42 * 17?",
    "Search for info about Python",
    "Read notes.txt and tell me how many known issues are listed",
    "How many characters are in the word 'LangChain'?",
    "What is 100 + 200 + 300?",
]

if __name__ == "__main__":
    print("=" * 70)
    print("HEAD-TO-HEAD: Framework (LangChain) vs Raw (Gemini API)")
    print("=" * 70)
    
    fw_results = []
    raw_results = []
    
    for i, query in enumerate(TEST_QUERIES):
        print(f"\n--- Query {i+1}: {query[:60]} ---")
        
        # Framework
        fw_answer, fw_time = run_framework_agent(query)
        fw_results.append({"answer": fw_answer[:80], "time": fw_time})
        print(f"  Framework: {fw_answer[:60]}  ({fw_time:.2f}s)")
        
        # Raw
        raw_answer, raw_time = run_raw_agent(query)
        raw_results.append({"answer": raw_answer[:80], "time": raw_time})
        print(f"  Raw:       {raw_answer[:60]}  ({raw_time:.2f}s)")
    
    # Summary
    fw_avg = sum(r["time"] for r in fw_results) / len(fw_results)
    raw_avg = sum(r["time"] for r in raw_results) / len(raw_results)
    
    print(f"\n\n{'='*70}")
    print(f"RESULTS SUMMARY")
    print(f"{'='*70}")
    print(f"  Framework avg time: {fw_avg:.2f}s")
    print(f"  Raw avg time:       {raw_avg:.2f}s")
    print(f"  Difference:         {abs(fw_avg - raw_avg):.2f}s")
    
    print(f"""
{'='*70}
FINAL COMPARISON TABLE
{'='*70}

    ┌────────────────────┬─────────────────────┬─────────────────────┐
    │ Criterion          │ Framework           │ Raw                 │
    │                    │ (LangChain/LangGraph)│ (requests + Gemini) │
    ├────────────────────┼─────────────────────┼─────────────────────┤
    │ Lines of code      │ ~100                │ ~200                │
    │ Setup effort       │ Low (pip install)   │ None (stdlib+req)   │
    │ Tool creation      │ Easy (@tool)        │ Manual (JSON schema)│
    │ Debugging          │ Harder (abstractions)│ Easier (see all)   │
    │ Flexibility        │ Limited by framework│ Unlimited           │
    │ Community/Docs     │ Extensive           │ Just API docs       │
    │ Memory support     │ Built-in            │ DIY                 │
    │ Error handling     │ Some built-in       │ All DIY             │
    │ Switching LLMs     │ Change 1 import     │ Rewrite API calls   │
    │ Testing/Eval       │ LangSmith           │ DIY (file 05)       │
    ├────────────────────┼─────────────────────┼─────────────────────┤
    │ USE WHEN:          │ Production apps,    │ Learning, debugging,│
    │                    │ rapid prototyping,  │ custom behavior,    │
    │                    │ team collaboration  │ edge cases, control │
    └────────────────────┴─────────────────────┴─────────────────────┘
    
    THE KEY INSIGHT:
    Frameworks don't add capabilities. They organize and simplify.
    Everything a framework does, you can do in raw Python.
    But a framework saves time and reduces bugs.
    
    Now that you understand BOTH, you can:
    1. Use frameworks confidently (knowing what they hide)
    2. Debug framework issues (because you know the raw equivalent)
    3. Build custom behavior (when the framework is too restrictive)
    4. Switch frameworks easily (because you understand the patterns, not just the API)
    """)
