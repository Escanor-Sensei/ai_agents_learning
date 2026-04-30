"""
=============================================================================
DAY 3 - FILE 05: REFLECTION (Self-Evaluation with Framework)
=============================================================================

CONCEPT (5 lines):
- Agents can produce wrong or low-quality answers. Reflection catches this.
- Reflection = use the LLM to evaluate the LLM's own output.
- Pattern: Generate answer → Grade it (1-10) → If score < 7, retry with feedback.
- This is the LLM equivalent of code review: generate → review → revise.
- LangGraph makes this easy with conditional edges: answer → evaluate → retry OR done.

ANALOGY FOR .NET DEVS:
- Like unit testing your output before returning it.
- Generate response → run validation → if fails, regenerate.
- Conditional edge = if/else in a middleware pipeline.
=============================================================================
"""

import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

load_dotenv()

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))


# =========================
# STEP 1: Tools
# =========================

@tool
def calculator(expression: str) -> str:
    """Calculate a math expression. Input: a valid Python expression."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

@tool
def search_web(query: str) -> str:
    """Search the web for information. Input: a search query string."""
    SEARCH_DB = {
        "python": "Python is a high-level programming language. Created by Guido van Rossum in 1991. Latest: 3.12. Used for web, AI, data science, automation.",
        "machine learning": "Machine learning is a subset of AI where systems learn from data. Types: supervised, unsupervised, reinforcement learning.",
        "react pattern": "ReAct = Reasoning + Acting. An agent pattern from Yao et al. 2022.",
    }
    for key, val in SEARCH_DB.items():
        if key in query.lower():
            return val
    return f"No results for: {query}"


# =========================
# STEP 2: Define the state for our graph
# =========================

class AgentState(TypedDict):
    query: str
    answer: str
    critique: str
    score: int
    attempt: int
    max_attempts: int
    messages: list


# =========================
# STEP 3: Build the graph nodes
# =========================

def generate_answer(state: AgentState) -> dict:
    """Node 1: Generate an answer to the query."""
    query = state["query"]
    attempt = state.get("attempt", 1)
    critique = state.get("critique", "")
    
    if critique:
        prompt = f"""Answer this query: {query}

Your previous answer was criticized:
{critique}

Please provide an improved answer addressing the feedback. Be thorough and accurate."""
    else:
        prompt = f"Answer this query thoroughly and accurately: {query}"
    
    response = llm.invoke(prompt)
    
    print(f"\n  [Attempt {attempt}] Generated answer: {response.content[:150]}...")
    
    return {
        "answer": response.content,
        "attempt": attempt,
    }


def evaluate_answer(state: AgentState) -> dict:
    """Node 2: Evaluate the quality of the answer."""
    query = state["query"]
    answer = state["answer"]
    
    eval_prompt = f"""You are a strict quality evaluator. Grade this answer on a scale of 1-10.

Question: {query}
Answer: {answer}

Criteria:
1. Accuracy — Is the information correct?
2. Completeness — Does it fully answer the question?
3. Clarity — Is it well-organized and easy to understand?
4. Specificity — Does it include concrete details, not just vague statements?

Respond in this EXACT format:
SCORE: <number 1-10>
CRITIQUE: <specific feedback on what's wrong or missing>

Be strict! Only score 7+ if the answer is genuinely good."""

    response = llm.invoke(eval_prompt)
    eval_text = response.content
    
    # Parse score
    score = 5  # default
    critique = eval_text
    
    for line in eval_text.split("\n"):
        line = line.strip()
        if line.startswith("SCORE:"):
            try:
                score = int(line.split(":")[1].strip().split("/")[0].strip())
            except (ValueError, IndexError):
                score = 5
        elif line.startswith("CRITIQUE:"):
            critique = line.split(":", 1)[1].strip()
    
    print(f"  [Evaluation] Score: {score}/10")
    print(f"  [Evaluation] Critique: {critique[:100]}")
    
    return {
        "score": score,
        "critique": critique,
        "attempt": state["attempt"] + 1,
    }


def should_retry(state: AgentState) -> str:
    """Conditional edge: retry if score < 7 and attempts remain."""
    score = state.get("score", 0)
    attempt = state.get("attempt", 1)
    max_attempts = state.get("max_attempts", 3)
    
    if score >= 7:
        print(f"  [Decision] Score {score} >= 7 → ACCEPT answer")
        return "accept"
    elif attempt > max_attempts:
        print(f"  [Decision] Max attempts ({max_attempts}) reached → ACCEPT best effort")
        return "accept"
    else:
        print(f"  [Decision] Score {score} < 7, attempt {attempt}/{max_attempts} → RETRY")
        return "retry"


# =========================
# STEP 4: Build the LangGraph graph
# =========================

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("generate", generate_answer)
workflow.add_node("evaluate", evaluate_answer)

# Add edges
workflow.set_entry_point("generate")
workflow.add_edge("generate", "evaluate")

# Conditional edge after evaluation
workflow.add_conditional_edges(
    "evaluate",
    should_retry,
    {
        "retry": "generate",   # Loop back to generate
        "accept": END,         # Done!
    }
)

# Compile the graph
reflection_agent = workflow.compile()


# =========================
# STEP 5: Test the reflection loop
# =========================

def run_with_reflection(query: str):
    print(f"\n{'='*60}")
    print(f"REFLECTION AGENT")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    result = reflection_agent.invoke({
        "query": query,
        "answer": "",
        "critique": "",
        "score": 0,
        "attempt": 1,
        "max_attempts": 3,
        "messages": [],
    })
    
    print(f"\n  FINAL: Score={result['score']}, Attempts={result['attempt']-1}")
    print(f"  Answer: {result['answer'][:300]}")
    return result


if __name__ == "__main__":
    # Test 1: Straightforward query (should pass first try)
    run_with_reflection("What is 2 + 2?")
    
    print("\n")
    
    # Test 2: Complex query (might need improvement)
    run_with_reflection(
        "Explain the difference between supervised and unsupervised machine learning with examples"
    )
    
    print("\n")
    
    # Test 3: Question requiring depth (likely to get critiqued)
    run_with_reflection(
        "What are the pros and cons of using AI agents vs traditional software for task automation?"
    )

    print("""
    THE REFLECTION PATTERN:
    
    ┌──────────┐      ┌──────────┐      ┌───────────┐
    │ Generate │ ───→ │ Evaluate │ ───→ │ Score ≥ 7 │ ───→ DONE
    │ Answer   │      │ Answer   │      │    ?      │
    └──────────┘      └──────────┘      └───────────┘
         ↑                                    │ No
         └────────────────────────────────────┘
                  (with critique feedback)
    """)

    # KEY OBSERVATION:
    # - Reflection adds 1 extra LLM call per attempt (the evaluation)
    # - The critique is SPECIFIC feedback — not just "try again"
    # - The evaluator can be stricter or lenient depending on the prompt
    # - This is expensive (2-6 LLM calls per query) but produces better answers
    # - Risk: the evaluator might be wrong (LLM checking LLM has blind spots)
    #
    # → File 06: Build reflection from scratch (raw Gemini API)
