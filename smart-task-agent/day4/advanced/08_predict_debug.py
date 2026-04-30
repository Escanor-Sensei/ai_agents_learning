"""
=============================================================================
DAY 4 - FILE 08: PREDICT & DEBUG (Final Debugging Exercises)
=============================================================================

For each exercise:
1. READ the code carefully
2. PREDICT what will happen (write it down!)
3. EXPLAIN why
4. Then run to verify

These are the trickiest bugs — they combine issues from all 4 days.
=============================================================================
"""

import os
import json
import time
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


def call_gemini(contents, tools=None, system=None):
    body = {"contents": contents}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    if tools:
        body["tools"] = [{"functionDeclarations": tools}]
    resp = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, json=body, timeout=30)
    return resp.json()


# ================================================================
# EXERCISE 1: The Wrong Cache + Reflection Combo
# ================================================================
def exercise_1():
    """
    PREDICT: What happens when memory returns stale data and 
    reflection always says it's fine?
    """
    print("\n" + "="*60)
    print("EXERCISE 1: Wrong Cache + Reflection")
    print("="*60)
    
    # Memory cache with OUTDATED info
    memory_cache = {
        "python version": "The latest Python version is 3.8.",  # WRONG — it's 3.12+
        "best framework": "Django is the only web framework for Python.",  # WRONG
    }
    
    # Reflection that ALWAYS passes
    def always_pass_reflection(query, answer):
        return {"score": 10, "passed": True, "reason": "Looks great!"}
    
    # Agent that checks cache first
    def run_cached_agent(query):
        # Check cache
        for key in memory_cache:
            if key in query.lower():
                cached = memory_cache[key]
                print(f"  [cache hit] Returning: {cached}")
                
                # Reflect
                reflection = always_pass_reflection(query, cached)
                print(f"  [reflection] Score: {reflection['score']} — {reflection['reason']}")
                
                return cached
        
        # No cache hit — call LLM
        data = call_gemini([{"role": "user", "parts": [{"text": query}]}])
        answer = data["candidates"][0]["content"]["parts"][0]["text"]
        return answer
    
    # Test
    result = run_cached_agent("What is the latest Python version?")
    print(f"\n  Answer: {result}")
    
    print("""
    YOUR PREDICTION:
    _________________________________________________
    
    WHAT ACTUALLY HAPPENS:
    - The cache returns stale info ("Python 3.8")
    - Reflection says "Score: 10, looks great!" (always passes)
    - The agent confidently returns WRONG information
    - Two safety mechanisms BOTH failed
    
    LESSON: Memory needs expiry/validation. Reflection needs real evaluation.
    A broken safety net is worse than no safety net — it gives false confidence.
    """)


# ================================================================
# EXERCISE 2: Mid-Plan Tool Failure
# ================================================================
def exercise_2():
    """
    PREDICT: What happens when one step in a multi-step plan fails?
    """
    print("\n" + "="*60)
    print("EXERCISE 2: Mid-Plan Tool Failure")
    print("="*60)
    
    plan = [
        "Step 1: Calculate 100 * 25",
        "Step 2: Read the result file (results.txt)",  # This file doesn't exist!
        "Step 3: Summarize both pieces of information",
    ]
    
    def execute_step(step):
        if "calculate" in step.lower():
            return "2500"
        elif "read" in step.lower():
            raise FileNotFoundError("results.txt not found")
        elif "summarize" in step.lower():
            return "Summary of collected information"
    
    print("  Executing plan...")
    results = []
    for step in plan:
        print(f"  → {step}")
        try:
            result = execute_step(step)
            results.append({"step": step, "result": result, "status": "ok"})
            print(f"    ✓ {result}")
        except Exception as e:
            results.append({"step": step, "result": str(e), "status": "error"})
            print(f"    ✗ Error: {e}")
            # BUG: We continue executing! Step 3 doesn't know Step 2 failed.
    
    # Step 3 runs but its "summary" is meaningless without Step 2's data
    print(f"\n  Plan results: {json.dumps(results, indent=2)}")
    
    print("""
    YOUR PREDICTION:
    _________________________________________________
    
    WHAT ACTUALLY HAPPENS:
    - Step 1 succeeds: "2500"
    - Step 2 FAILS: FileNotFoundError
    - Step 3 runs anyway and produces a generic "summary"
    - The final answer is INCOMPLETE but looks correct
    
    LESSON: When a plan step fails, you need to either:
    1. RE-PLAN (adjust remaining steps)
    2. ABORT (if the failed step was critical)
    3. SKIP (if the step was optional)
    Never just continue blindly — downstream steps depend on upstream results.
    """)


# ================================================================
# EXERCISE 3: Blind-Spot Reflection
# ================================================================
def exercise_3():
    """
    PREDICT: What happens when reflection checks the WRONG thing?
    """
    print("\n" + "="*60)
    print("EXERCISE 3: Blind-Spot Reflection")
    print("="*60)
    
    def reflect_on_length(query, answer):
        """This reflection only checks answer LENGTH, not correctness."""
        if len(answer) > 20:
            return {"score": 9, "passed": True, "reason": "Answer is detailed enough"}
        else:
            return {"score": 3, "passed": False, "reason": "Answer too short"}
    
    # A long but WRONG answer
    wrong_answer = "The capital of France is Berlin, which is a beautiful city located in the heart of Europe with many historical landmarks and cultural attractions."
    
    # A short but CORRECT answer
    correct_answer = "Paris"
    
    wrong_eval = reflect_on_length("What is the capital of France?", wrong_answer)
    correct_eval = reflect_on_length("What is the capital of France?", correct_answer)
    
    print(f"  Wrong answer ({len(wrong_answer)} chars): Score {wrong_eval['score']} — {wrong_eval['reason']}")
    print(f"  Correct answer ({len(correct_answer)} chars): Score {correct_eval['score']} — {correct_eval['reason']}")
    
    print("""
    YOUR PREDICTION:
    _________________________________________________
    
    WHAT ACTUALLY HAPPENS:
    - Wrong answer "Berlin..." gets Score 9 (PASS) because it's long
    - Correct answer "Paris" gets Score 3 (FAIL) because it's short
    - Reflection REJECTS the correct answer and ACCEPTS the wrong one!
    
    LESSON: Reflection must evaluate CORRECTNESS, not surface features.
    Common blind spots: length, confidence tone, keyword presence.
    LLM-as-judge is better because it understands the QUESTION.
    """)


# ================================================================
# EXERCISE 4: Infinite Tool Loop
# ================================================================
def exercise_4():
    """
    PREDICT: What happens when a tool result triggers another tool call
    in an endless cycle?
    """
    print("\n" + "="*60)
    print("EXERCISE 4: Infinite Tool Loop")
    print("="*60)
    
    iteration = 0
    max_iterations = 5  # Safety limit for demo
    
    def search_tool(query):
        return f"Results for '{query}': See more details by searching '{query} details'"
    
    def agent_loop(query):
        nonlocal iteration
        current_query = query
        results = []
        
        while iteration < max_iterations:
            iteration += 1
            print(f"  Iteration {iteration}: searching '{current_query[:40]}'")
            
            result = search_tool(current_query)
            results.append(result)
            
            # Simulate LLM deciding to search again based on "See more details"
            if "See more details" in result:
                # Extract the suggested next query
                next_q = result.split("searching '")[1].rstrip("'")
                current_query = next_q
                print(f"    → LLM decides to search again: '{next_q[:40]}'")
                # Loop continues!
            else:
                break
        
        if iteration >= max_iterations:
            print(f"  ⚠ Hit max iterations ({max_iterations})")
        
        return results
    
    results = agent_loop("latest AI news")
    print(f"\n  Total API calls: {iteration}")
    print(f"  Last result: {results[-1][:80]}...")
    
    print("""
    YOUR PREDICTION:
    _________________________________________________
    
    WHAT ACTUALLY HAPPENS:
    - Search returns "See more details by searching 'X details'"
    - LLM interprets this as "I should search again"
    - Next search returns "See more details by searching 'X details details'"
    - Loop repeats: query grows longer each time
    - Without max_iterations, this would run FOREVER (and burn API credits)
    
    LESSON: Tool results can accidentally trigger loops. Defenses:
    1. max_iterations (hard limit)
    2. Track recent tool calls (detect repetition — see day4/04_error_handling.py)
    3. Instruct the LLM: "Do not call the same tool more than 2 times"
    4. Rate limit: track API calls and pause if too many
    """)


# =========================
# Run all exercises
# =========================
if __name__ == "__main__":
    print("DAY 4 — PREDICT & DEBUG EXERCISES")
    print("For each exercise: PREDICT first, then run to verify!\n")
    
    exercise_1()
    exercise_2()
    exercise_3()
    exercise_4()
    
    print(f"""
{'='*60}
SUMMARY OF ALL DAY 4 DEBUG EXERCISES
{'='*60}

    ┌──────┬──────────────────────────────────────────────────┐
    │  #   │ Bug / Lesson                                     │
    ├──────┼──────────────────────────────────────────────────┤
    │  1   │ Stale cache + always-pass reflection = confident │
    │      │ wrong answers. Both safeguards failed.           │
    ├──────┼──────────────────────────────────────────────────┤
    │  2   │ Mid-plan failure + blind continuation = partial  │
    │      │ answer that looks complete. Need re-planning.    │
    ├──────┼──────────────────────────────────────────────────┤
    │  3   │ Surface-level reflection (length) rejects right  │
    │      │ answers and accepts wrong ones. Check MEANING.   │
    ├──────┼──────────────────────────────────────────────────┤
    │  4   │ Tool results trigger more tool calls → infinite  │
    │      │ loop. Need max iterations + repetition detection.│
    └──────┴──────────────────────────────────────────────────┘
    
    These are REAL bugs in production agent systems.
    Knowing these patterns will save you hours of debugging.
    """)
