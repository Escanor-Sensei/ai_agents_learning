"""
=============================================================================
DAY 3 - FILE 06: RAW REFLECTION (Two-Call Pattern, No Framework)
=============================================================================

CONCEPT (5 lines):
- File 05 used LangGraph to build the reflection loop. Here: raw API calls.
- Pattern: Call 1 (generate) → Call 2 (evaluate) → if bad, Call 3 (regenerate).
- The "evaluator" is just another LLM call with a different prompt.
- Max 3 retries to prevent infinite loops and runaway costs.
- This is the simplest self-improvement pattern. More advanced: tree-of-thought, debate.

ANALOGY FOR .NET DEVS:
- Like retry with Polly, but the retry logic is an LLM call, not a simple condition.
- Generate = service call. Evaluate = health check. Retry = Polly RetryAsync.
=============================================================================
"""

import os
import json
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
# STEP 1: LLM helper
# =========================

def call_llm(prompt: str) -> str:
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
    }
    response = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, json=body)
    if response.status_code != 200:
        raise Exception(f"API error {response.status_code}: {response.text}")
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


# =========================
# STEP 2: Generate answer
# =========================

def generate_answer(query: str, critique: str = "") -> str:
    """Generate an answer. If critique provided, incorporate feedback."""
    if critique:
        prompt = f"""Answer this question: {query}

Your previous answer was reviewed and received this feedback:
{critique}

Please provide an IMPROVED answer that addresses all the feedback points.
Be thorough, accurate, and specific."""
    else:
        prompt = f"Answer this question thoroughly and accurately: {query}"
    
    return call_llm(prompt)


# =========================
# STEP 3: Evaluate answer
# =========================

def evaluate_answer(query: str, answer: str) -> tuple:
    """
    Evaluate the answer quality.
    Returns: (score: int, critique: str)
    """
    eval_prompt = f"""You are a strict answer evaluator. Grade this answer 1-10.

QUESTION: {query}

ANSWER: {answer}

CRITERIA:
1. Accuracy (is it factually correct?)
2. Completeness (does it fully answer the question?)
3. Clarity (well-organized, easy to understand?)
4. Specificity (concrete examples and details?)

RESPOND IN EXACTLY THIS FORMAT:
SCORE: <integer 1-10>
CRITIQUE: <what needs improvement — be specific>

Be strict. 7+ means genuinely good. 5-6 means mediocre. Below 5 means poor."""

    response = call_llm(eval_prompt)
    
    # Parse the response
    score = 5
    critique = response
    
    for line in response.split("\n"):
        line = line.strip()
        if line.upper().startswith("SCORE:"):
            try:
                score_text = line.split(":")[1].strip()
                # Handle "8/10" or just "8"
                score = int(score_text.split("/")[0].strip())
                score = max(1, min(10, score))  # Clamp to 1-10
            except (ValueError, IndexError):
                score = 5
        elif line.upper().startswith("CRITIQUE:"):
            critique = line.split(":", 1)[1].strip()
    
    return score, critique


# =========================
# STEP 4: The reflection loop
# =========================

def reflect_and_improve(query: str, max_attempts: int = 3, min_score: int = 7) -> dict:
    """
    Generate → Evaluate → Retry if needed.
    
    Returns dict with: answer, score, attempts, history
    """
    
    print(f"\n{'='*60}")
    print(f"RAW REFLECTION AGENT")
    print(f"Query: {query}")
    print(f"Target score: {min_score}+/10 | Max attempts: {max_attempts}")
    print(f"{'='*60}")
    
    history = []
    critique = ""
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n--- Attempt {attempt}/{max_attempts} ---")
        
        # Generate answer
        answer = generate_answer(query, critique)
        print(f"  Answer: {answer[:150]}...")
        
        # Evaluate
        score, critique = evaluate_answer(query, answer)
        print(f"  Score: {score}/10")
        print(f"  Critique: {critique[:100]}")
        
        history.append({
            "attempt": attempt,
            "answer": answer[:200],
            "score": score,
            "critique": critique[:200]
        })
        
        # Check if good enough
        if score >= min_score:
            print(f"\n✓ Score {score} >= {min_score} — ACCEPTED on attempt {attempt}")
            return {
                "answer": answer,
                "score": score,
                "attempts": attempt,
                "history": history,
                "accepted": True
            }
        else:
            print(f"  Score {score} < {min_score} — will retry with feedback")
    
    # Max attempts reached — return best answer
    best = max(history, key=lambda h: h["score"])
    print(f"\n✗ Max attempts reached. Best score: {best['score']}/10 on attempt {best['attempt']}")
    
    return {
        "answer": history[-1]["answer"],  # Return last attempt
        "score": history[-1]["score"],
        "attempts": max_attempts,
        "history": history,
        "accepted": False
    }


# =========================
# STEP 5: Test
# =========================
if __name__ == "__main__":
    # Test 1: Easy question (should pass first try)
    result1 = reflect_and_improve("What is the capital of France?")
    
    print("\n\n")
    
    # Test 2: Harder question (might need retries)
    result2 = reflect_and_improve(
        "Explain the differences between ReAct and Plan-then-Execute agent patterns, with examples of when to use each"
    )
    
    print("\n\n")
    
    # Test 3: Very strict threshold
    result3 = reflect_and_improve(
        "What are three specific ways that AI agents differ from traditional chatbots?",
        max_attempts=3,
        min_score=8  # Very strict!
    )
    
    # Show improvement history
    print("\n\n" + "=" * 60)
    print("IMPROVEMENT HISTORY (Test 2)")
    print("=" * 60)
    for h in result2["history"]:
        print(f"  Attempt {h['attempt']}: Score {h['score']}/10")
        print(f"    Critique: {h['critique'][:80]}")
    
    print("""
    THE RAW REFLECTION PATTERN:
    
    ┌─────────────┐
    │ 1. Generate │──→ answer = call_llm(query + critique)
    └──────┬──────┘
           ▼
    ┌─────────────┐
    │ 2. Evaluate │──→ score, critique = call_llm(evaluate_prompt)
    └──────┬──────┘
           ▼
    ┌─────────────┐    score >= 7?  ──→  DONE ✓
    │ 3. Decide   │
    └──────┬──────┘    score < 7 and attempts left?  ──→  go to 1 (with critique)
           ▼
    Max attempts reached?  ──→  Return best effort ✗
    
    
    COST:  Each attempt = 2 LLM calls (generate + evaluate)
           3 attempts = 6 LLM calls total
           
    RISK:  Evaluator LLM might be wrong (give 9/10 to bad answer, or 3/10 to good answer)
           This is a fundamental limitation: the judge uses the same model as the generator.
           Fix: use a stronger model as evaluator, or use human evaluation.
    """)

    # KEY OBSERVATION:
    # - Reflection is just "use the LLM to check the LLM" — no magic
    # - The critique is what makes retries effective (not just "try again")
    # - Strict evaluators improve quality but cost more (more retries)
    # - This pattern works best when the evaluator is better than the generator
    #
    # → File 07: YOUR TASK — Add memory + reflection to the Smart Task Agent
