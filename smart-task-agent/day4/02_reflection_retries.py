"""
=============================================================================
DAY 4 - FILE 02: REFLECTION & RETRIES — Self-Improving Agents
=============================================================================

CONCEPT:
- An agent can evaluate its OWN output and retry if it's not good enough.
- Reflection = "was my answer good?" (self-critique after generating)
- Retry = "let me try again with feedback" (loop until quality threshold)
- Without reflection: agent gives first answer, right or wrong.
- With reflection: agent gives answer → scores it → improves → repeats.
- Always set max_retries to prevent infinite loops.

ANALOGY FOR .NET DEVS:
- Reflection = unit tests that run AFTER your code generates output.
- Retry = Polly retry policy: if response doesn't meet criteria, try again.
- Max retries = circuit breaker: stop after N failures.

WHY THIS MATTERS:
- LLMs are probabilistic — first answer isn't always best.
- Reflection catches errors the LLM would otherwise miss.
- Combined with tools: act → observe → reflect → retry if needed.
=============================================================================
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))


# =========================
# STEP 1: Without reflection (naive — one shot)
# =========================

print("=" * 60)
print("WITHOUT REFLECTION: First answer, take it or leave it")
print("=" * 60)

query = "Explain what an AI agent is in exactly 3 bullet points."
response = llm.invoke(query)
print(f"\n  Query: {query}")
print(f"  Answer:\n{response.content}")
bullet_count = response.content.count("•") + response.content.count("-") + response.content.count("*")
print(f"\n  Bullet points found: ~{bullet_count}")
print("  → Maybe 3, maybe not. No quality check.")


# =========================
# STEP 2: Simple evaluator function
# =========================

def evaluate(query: str, answer: str) -> tuple[int, str]:
    """Score an answer 1-10 and give feedback."""
    eval_prompt = f"""Score this answer from 1-10 and give one-line feedback.

Question: {query}
Answer: {answer}

Respond in EXACTLY this format:
SCORE: <number>
FEEDBACK: <one line>"""

    result = llm.invoke(eval_prompt)
    text = result.content.strip()

    # Parse score
    score = 5  # default
    feedback = "No feedback"
    for line in text.split("\n"):
        if line.strip().startswith("SCORE:"):
            try:
                score = int(line.split(":")[1].strip().split()[0])
            except (ValueError, IndexError):
                pass
        elif line.strip().startswith("FEEDBACK:"):
            feedback = line.split(":", 1)[1].strip()

    return score, feedback


# =========================
# STEP 3: Reflection loop (generate → evaluate → retry)
# =========================

print("\n\n" + "=" * 60)
print("WITH REFLECTION: Generate → Evaluate → Retry if needed")
print("=" * 60)

query = "Explain what an AI agent is in exactly 3 bullet points."
max_retries = 3
threshold = 7

print(f"\n  Query: {query}")
print(f"  Threshold: {threshold}/10, Max retries: {max_retries}\n")

feedback = ""
for attempt in range(1, max_retries + 1):
    # Generate (include feedback from previous attempt)
    prompt = query
    if feedback:
        prompt += f"\n\nPrevious attempt was scored low. Feedback: {feedback}\nPlease improve."

    answer = llm.invoke(prompt).content

    # Evaluate
    score, feedback = evaluate(query, answer)

    print(f"  Attempt {attempt}:")
    print(f"    Score: {score}/10")
    print(f"    Feedback: {feedback}")
    print(f"    Answer: {answer[:120]}...")

    if score >= threshold:
        print(f"\n  ✓ Accepted on attempt {attempt}!")
        break
else:
    print(f"\n  ✗ Max retries ({max_retries}) reached. Using last answer.")
    print("  LESSON: Always cap retries — the evaluator might be too strict!")


print(f"""
=============================================================================
DEEP THEORY: Reflection Patterns
=============================================================================

1. THE REFLECTION LOOP
   ┌──────────────────────────────────────────────────────────┐
   │  Generate answer                                         │
   │       ↓                                                  │
   │  Evaluate (score + feedback)                             │
   │       ↓                                                  │
   │  Score >= threshold? ──YES──→ Return answer              │
   │       │                                                  │
   │      NO                                                  │
   │       ↓                                                  │
   │  Retry with feedback (up to max_retries)                 │
   └──────────────────────────────────────────────────────────┘

2. THREE TYPES OF REFLECTION
   ┌─────────────────────────┬──────────────────────────────────┐
   │ Type                    │ How it works                     │
   ├─────────────────────────┼──────────────────────────────────┤
   │ Self-reflection         │ Same LLM scores its own output.  │
   │                         │ Simple but biased (may be lenient│
   │                         │ on its own mistakes).            │
   ├─────────────────────────┼──────────────────────────────────┤
   │ External evaluator      │ Different LLM or rule-based      │
   │                         │ checker scores the output.        │
   │                         │ More objective but more LLM calls│
   ├─────────────────────────┼──────────────────────────────────┤
   │ Tool-based validation   │ Use code/tests to verify output. │
   │                         │ E.g., run SQL, check JSON format.│
   │                         │ Most reliable for structured data│
   └─────────────────────────┴──────────────────────────────────┘

3. RETRY STRATEGIES
   - Fixed retry: try up to N times, always the same way
   - Retry with feedback: include evaluator's critique in next prompt
   - Exponential backoff: wait longer between retries (for rate limits)
   - Fallback: after max retries, use a different approach entirely

4. WHEN TO USE REFLECTION
   ✓ Complex generation (essays, code, plans) — worth the extra LLM calls
   ✓ When output format matters (JSON, bullet points, word count)
   ✓ When correctness is critical (medical, legal, financial)
   ✗ Simple factual Q&A — reflection adds cost with little benefit
   ✗ Real-time chat — latency of 2-3x is noticeable

5. COST ANALYSIS
   Without reflection: 1 LLM call
   With reflection (max 3 retries): up to 7 LLM calls (3 generate + 3 evaluate + 1 if accepted early)
   → 3-7x more expensive. Use selectively.

6. REFLECTION + TOOLS (The Full Agent Pattern)
   In a ReAct agent, reflection happens naturally:
   - Tool returns error → LLM "reflects" on the error → retries with different input
   - This is implicit reflection — the LLM adapts based on tool feedback
   - Explicit reflection adds a scoring step on top of that

=============================================================================
""")
