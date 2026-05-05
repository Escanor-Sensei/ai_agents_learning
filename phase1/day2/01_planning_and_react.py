"""
=============================================================================
DAY 2 - FILE 01: PLANNING & ReAct — Two Agent Strategies
=============================================================================

CONCEPT:
- ReAct (Day 1): Think → Act → Observe → Repeat. One step at a time.
- Plan-then-Execute: Make a FULL PLAN first → Execute ALL steps → Done.
- ReAct is flexible (adapts mid-way) but slow (many LLM calls).
- Plan-then-Execute is faster (fewer LLM calls) but rigid (can't adapt).
- Real systems combine both: plan first, then ReAct within each step.

ANALOGY FOR .NET DEVS:
- ReAct = debugging step-by-step with F11 (Step Into). Flexible but slow.
- Plan-then-Execute = writing a script to run tests in order. Fast but rigid.
=============================================================================
"""

import os
import json
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from _tools import calculator, get_word_length, search_web, read_file, get_current_time, ALL_TOOLS, trace_messages, count_calls, get_final_answer

load_dotenv()

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))

# A query that requires 2 tool calls in sequence
TEST_QUERY = "How many characters are in 'intelligence'? Then multiply that count by 7."


# =========================
# APPROACH 1: ReAct (step-by-step, no upfront plan)
# =========================

print("=" * 60)
print("APPROACH 1: ReAct (step-by-step, no upfront plan)")
print("=" * 60)
print(f"Query: {TEST_QUERY}\n")

start = time.time()
react_agent = create_react_agent(model=llm, tools=[calculator, get_word_length])
react_result = react_agent.invoke({"messages": [("human", TEST_QUERY)]})
react_time = time.time() - start

react_llm, react_tools = count_calls(react_result)
trace_messages(react_result)
print(f"\n  LLM calls: {react_llm}, Tool calls: {react_tools}, Time: {react_time:.1f}s")


# =========================
# APPROACH 2: Plan-then-Execute (plan first, then run)
# =========================

print("\n\n" + "=" * 60)
print("APPROACH 2: Plan-then-Execute (plan first, then run)")
print("=" * 60)
print(f"Query: {TEST_QUERY}\n")

start = time.time()

# Phase 1: PLANNING (one LLM call — no tools, just a JSON plan)
planning_prompt = f"""You are a planning assistant. Create a step-by-step plan for this query.
Do NOT execute anything — just plan.

Available tools:
- calculator: Calculate math expressions (input: Python expression)
- get_word_length: Count characters in text (input: word or phrase)

Query: {TEST_QUERY}

Respond with ONLY a JSON array:
[
  {{"step": 1, "tool": "tool_name", "input": "tool_input", "purpose": "why"}},
  {{"step": 2, "tool": "tool_name", "input": "use result from step 1", "purpose": "why"}}
]"""

print("--- Phase 1: Planning ---")
plan_response = llm.invoke(planning_prompt)
plan_text = plan_response.content

try:
    start_idx = plan_text.find("[")
    end_idx = plan_text.rfind("]") + 1
    plan = json.loads(plan_text[start_idx:end_idx]) if start_idx >= 0 else []
except (json.JSONDecodeError, ValueError):
    plan = []

for step in plan:
    print(f"  Step {step['step']}: {step['tool']}({step.get('input', '')[:50]}) — {step.get('purpose', '')}")

# Phase 2: EXECUTION
print("\n--- Phase 2: Execution ---")
TOOL_MAP = {"calculator": calculator, "get_word_length": get_word_length}
step_results = {}

for step in plan:
    tool_name = step["tool"]
    tool_input = step.get("input", "")
    depends = step.get("depends_on")
    if depends and depends in step_results:
        tool_input = str(step_results[depends])

    if tool_name in TOOL_MAP:
        result = TOOL_MAP[tool_name].invoke(tool_input)
        step_results[step["step"]] = result
        print(f"  Step {step['step']}: {tool_name}({tool_input[:50]}) → {result}")

plan_time = time.time() - start
print(f"\n  LLM calls: 2 (plan + synthesis), Tool calls: {len(plan)}, Time: {plan_time:.1f}s")


# =========================
# COMPARISON
# =========================

print("\n\n" + "=" * 60)
print("COMPARISON")
print("=" * 60)
print(f"""
  {'Metric':<25} {'ReAct':<20} {'Plan-then-Execute':<20}
  {'─'*25} {'─'*20} {'─'*20}
  {'LLM calls':<25} {react_llm:<20} {'2':<20}
  {'Tool calls':<25} {react_tools:<20} {len(plan):<20}
  {'Time (seconds)':<25} {react_time:<20.1f} {plan_time:<20.1f}
""")


print("""
=============================================================================
DEEP THEORY: ReAct vs Plan-then-Execute vs Hybrid
=============================================================================

1. ReAct (Reasoning + Acting)
   ┌──────────────────────────────────────────────────────────┐
   │ Human → LLM thinks → calls tool → observes → thinks     │
   │        → calls tool → observes → gives final answer      │
   └──────────────────────────────────────────────────────────┘
   - Each step: LLM sees ALL previous messages (history grows)
   - LLM DECIDES the flow — you can't predict how many steps
   - Flexible: handles surprises mid-way (tool error, unexpected data)
   - Slow: each step = 1 LLM API call = ~1-3 seconds
   - Expensive: tokens grow each iteration (history resent every time)
   - Used by: LangChain create_react_agent, most chatbot agents

2. Plan-then-Execute
   ┌──────────────────────────────────────────────────────────┐
   │ Phase 1: LLM generates full plan as JSON (1 LLM call)   │
   │ Phase 2: Execute each step mechanically (no LLM needed) │
   │ Phase 3: LLM synthesizes final answer (1 LLM call)      │
   └──────────────────────────────────────────────────────────┘
   - Faster: 2-3 LLM calls total vs N+1 for ReAct
   - Cheaper: less token usage overall
   - Rigid: if step 2 fails, the whole plan is invalid
   - Used by: AutoGPT, BabyAGI, Plan-and-Solve prompting

3. Hybrid (what production systems use)
   ┌──────────────────────────────────────────────────────────┐
   │ Phase 1: Plan first (get a roadmap)                      │
   │ Phase 2: Execute each step using ReAct (handle surprises)│
   │ Phase 3: If a step fails → RE-PLAN from current state    │
   └──────────────────────────────────────────────────────────┘
   - Best of both: structure of planning + flexibility of ReAct
   - Re-planning: "Here's what worked, here's what failed. New plan?"
   - Max replans: typically 2-3 to prevent infinite re-planning

4. WHEN TO USE WHICH
   ┌─────────────────────────┬─────────────────────────────┐
   │ ReAct                   │ Plan-then-Execute           │
   ├─────────────────────────┼─────────────────────────────┤
   │ Vague/open-ended query  │ Clear multi-step task       │
   │ Steps depend on results │ Independent steps           │
   │ Need flexibility        │ Need speed/cost savings     │
   │ Debugging/exploration   │ Batch processing            │
   └─────────────────────────┴─────────────────────────────┘

5. UNDER THE HOOD: Raw Planning Agent
   - Plan Generation: LLM returns JSON array of {step, tool, input, purpose}
   - Plan Execution: iterate steps, call tools, store results
   - Result Substitution: step 2's input can reference step 1's result
   - Re-planning: on failure, send new prompt with current context
   - Plan Validation: check tool names exist before executing
   - The framework code hides all this — it's just prompt + JSON + loop

=============================================================================
""")
