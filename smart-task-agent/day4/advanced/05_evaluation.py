"""
=============================================================================
DAY 4 - FILE 05: EVALUATION (Is Your Agent Actually Good?)
=============================================================================

CONCEPT (5 lines):
- You built an agent. But how do you know it works correctly?
- Evaluation = run a test suite, score each answer, print a report card.
- Scoring methods: exact match, keyword presence, LLM-as-judge.
- Evaluating agents is MUCH harder than evaluating functions (non-deterministic).
- This is the agent equivalent of unit tests — run before every deployment.

ANALOGY FOR .NET DEVS:
- Like integration tests for your API: send request, check response matches expected.
- LLM-as-judge = using a smarter model to validate the output (like a senior reviewer).
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
# STEP 1: Load eval suite
# =========================

def load_eval_suite() -> list:
    suite_path = os.path.join(os.path.dirname(__file__), "eval_suite.json")
    with open(suite_path, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================
# STEP 2: Build a simple agent for testing
# =========================

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
        "machine learning": "Machine learning is a subset of AI where systems learn from data.",
        "react pattern": "ReAct = Reasoning + Acting agent pattern.",
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
    "get_word_length": lambda args: get_word_length(args.get("word", "")),
    "search_web": lambda args: search_web(args.get("query", "")),
    "read_file": lambda args: read_file_tool(args.get("file_path", "")),
    "get_current_time": lambda args: get_current_time(args.get("format", "full")),
}

TOOL_DECLARATIONS = [
    {"name": "calculator", "description": "Calculate math expressions.",
     "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}},
    {"name": "get_word_length", "description": "Count characters in a word.",
     "parameters": {"type": "object", "properties": {"word": {"type": "string"}}, "required": ["word"]}},
    {"name": "search_web", "description": "Search web for information.",
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "read_file", "description": "Read a text file.",
     "parameters": {"type": "object", "properties": {"file_path": {"type": "string"}}, "required": ["file_path"]}},
    {"name": "get_current_time", "description": "Get current date/time.",
     "parameters": {"type": "object", "properties": {"format": {"type": "string"}}, "required": ["format"]}},
]


def run_agent(query: str, max_iterations: int = 8) -> str:
    """Simple agent for evaluation."""
    contents = [{"role": "user", "parts": [{"text": query}]}]
    
    for i in range(max_iterations):
        body = {
            "contents": contents,
            "tools": [{"functionDeclarations": TOOL_DECLARATIONS}],
            "systemInstruction": {"parts": [{"text": "You are a helpful assistant. Use tools when needed. Be concise."}]}
        }
        response = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, json=body)
        if response.status_code != 200:
            return f"API Error: {response.status_code}"
        
        data = response.json()
        parts = data["candidates"][0]["content"]["parts"]
        contents.append({"role": "model", "parts": parts})
        
        has_fc = False
        for part in parts:
            if "functionCall" in part:
                has_fc = True
                fc = part["functionCall"]
                name = fc["name"]
                args = fc.get("args", {})
                
                if name in TOOL_FUNCTIONS:
                    result = TOOL_FUNCTIONS[name](args)
                else:
                    result = f"Unknown tool: {name}"
                
                contents.append({"role": "user", "parts": [
                    {"functionResponse": {"name": name, "response": {"result": str(result)}}}
                ]})
        
        if not has_fc:
            return " ".join(p.get("text", "") for p in parts if "text" in p)
    
    return "Max iterations reached."


# =========================
# STEP 3: Scoring methods
# =========================

def score_keyword_match(answer: str, expected_keywords: list) -> dict:
    """Score based on presence of expected keywords."""
    answer_lower = answer.lower()
    found = [kw for kw in expected_keywords if kw.lower() in answer_lower]
    missing = [kw for kw in expected_keywords if kw.lower() not in answer_lower]
    
    score = len(found) / len(expected_keywords) if expected_keywords else 0
    
    return {
        "method": "keyword_match",
        "score": round(score, 2),
        "passed": score >= 0.5,  # At least half the keywords
        "found": found,
        "missing": missing,
    }


def score_llm_judge(query: str, answer: str) -> dict:
    """Use LLM to judge the answer quality (LLM-as-judge)."""
    judge_prompt = f"""You are an evaluator. Judge if this answer correctly addresses the question.

Question: {query}
Answer: {answer}

Respond with EXACTLY:
VERDICT: PASS or FAIL
SCORE: <1-10>
REASON: <one sentence explanation>"""
    
    body = {"contents": [{"role": "user", "parts": [{"text": judge_prompt}]}]}
    response = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, json=body)
    
    if response.status_code != 200:
        return {"method": "llm_judge", "score": 0, "passed": False, "reason": "Judge API call failed"}
    
    judge_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    
    verdict = "FAIL"
    score = 5
    reason = judge_text
    
    for line in judge_text.split("\n"):
        l = line.strip()
        if l.upper().startswith("VERDICT:"):
            verdict = "PASS" if "PASS" in l.upper() else "FAIL"
        elif l.upper().startswith("SCORE:"):
            try:
                score = int(l.split(":")[1].strip().split("/")[0].strip())
            except:
                score = 5
        elif l.upper().startswith("REASON:"):
            reason = l.split(":", 1)[1].strip()
    
    return {
        "method": "llm_judge",
        "score": score / 10,
        "passed": verdict == "PASS",
        "reason": reason[:100],
    }


# =========================
# STEP 4: Run evaluation
# =========================

def run_evaluation(use_llm_judge: bool = True) -> dict:
    """Run the full eval suite and print a scorecard."""
    
    suite = load_eval_suite()
    results = []
    
    print("=" * 70)
    print("EVALUATION SUITE — Smart Task Agent")
    print(f"Test cases: {len(suite)}")
    print(f"Scoring: keyword_match" + (" + llm_judge" if use_llm_judge else ""))
    print("=" * 70)
    
    for test in suite:
        test_id = test["id"]
        query = test["query"]
        keywords = test["expected_keywords"]
        category = test["category"]
        difficulty = test["difficulty"]
        
        print(f"\n  [{test_id:2d}] {category}/{difficulty}: {query[:60]}...")
        
        # Run agent
        t0 = time.time()
        try:
            answer = run_agent(query)
        except Exception as e:
            answer = f"AGENT ERROR: {e}"
        duration = time.time() - t0
        
        # Score: keyword match
        kw_score = score_keyword_match(answer, keywords)
        
        # Score: LLM judge (optional, costs extra API calls)
        llm_score = None
        if use_llm_judge:
            llm_score = score_llm_judge(query, answer)
        
        # Combined result
        passed = kw_score["passed"]
        if llm_score:
            passed = passed or llm_score["passed"]  # Pass if either method passes
        
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"       {status} | Keywords: {kw_score['score']:.0%}", end="")
        if llm_score:
            print(f" | Judge: {llm_score['score']:.0%} ({llm_score['reason'][:40]})", end="")
        print(f" | {duration:.1f}s")
        
        if kw_score.get("missing"):
            print(f"       Missing keywords: {kw_score['missing']}")
        
        results.append({
            "id": test_id,
            "query": query,
            "answer": answer[:200],
            "keyword_score": kw_score,
            "llm_score": llm_score,
            "passed": passed,
            "duration": duration,
        })
    
    # Print scorecard
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    
    easy = [r for r in results if suite[r["id"]-1]["difficulty"] == "easy"]
    medium = [r for r in results if suite[r["id"]-1]["difficulty"] == "medium"]
    hard = [r for r in results if suite[r["id"]-1]["difficulty"] == "hard"]
    
    print(f"\n{'='*70}")
    print(f"SCORECARD")
    print(f"{'='*70}")
    print(f"  Total:  {passed}/{total} passed ({passed/total:.0%})")
    print(f"  Easy:   {sum(1 for r in easy if r['passed'])}/{len(easy)}")
    print(f"  Medium: {sum(1 for r in medium if r['passed'])}/{len(medium)}")
    print(f"  Hard:   {sum(1 for r in hard if r['passed'])}/{len(hard)}")
    print(f"  Avg time: {sum(r['duration'] for r in results)/total:.1f}s per query")
    print(f"{'='*70}")
    
    if failed > 0:
        print(f"\n  Failed queries:")
        for r in results:
            if not r["passed"]:
                print(f"    [{r['id']}] {r['query'][:60]}")
    
    return {"total": total, "passed": passed, "results": results}


# =========================
# STEP 5: Run
# =========================
if __name__ == "__main__":
    # Run without LLM judge for speed (keyword only)
    print("Running evaluation (keyword scoring only)...\n")
    eval_result = run_evaluation(use_llm_judge=False)
    
    print("""
    EVALUATION METHODS COMPARISON:
    
    ┌─────────────────────┬───────────────────────────────────────┐
    │ Method              │ Tradeoffs                             │
    ├─────────────────────┼───────────────────────────────────────┤
    │ Exact match         │ Strict. Fails on rephrasing.          │
    │ Keyword presence    │ Flexible. Misses wrong context.       │
    │ LLM-as-judge        │ Smart. Expensive. Non-deterministic.  │
    │ Human evaluation    │ Best quality. Doesn't scale.          │
    ├─────────────────────┼───────────────────────────────────────┤
    │ Best practice:      │ Keyword for CI/CD + LLM for quality   │
    └─────────────────────┴───────────────────────────────────────┘
    
    KEY INSIGHT: Agent evaluation is fundamentally harder than testing
    regular functions because:
    1. Outputs are non-deterministic (different every run)
    2. Many correct answers exist (rephrasing, ordering)
    3. Quality is subjective (good enough vs perfect)
    4. Tool usage varies (same answer, different tool paths)
    """)

    # KEY OBSERVATION:
    # - A test suite is ESSENTIAL — run it before every change
    # - Keyword matching is cheap but crude; LLM judge is better but costly
    # - Real eval: combine automated metrics + human spot-checks
    # - This is the equivalent of "CI tests for your agent"
    #
    # → File 06: Framework vs Raw — final side-by-side comparison
