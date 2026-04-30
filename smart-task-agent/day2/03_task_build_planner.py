"""
=============================================================================
DAY 2 - FILE 04 (TASK): Build a Planning Agent with a Custom Tool
=============================================================================

INSTRUCTIONS:
Build a raw Python planning agent (no LangChain) that can:

1. Query a JSON "database" (sample_db.json) using a custom tool
2. Plan multi-step queries that combine database lookups with calculations
3. Execute the plan step-by-step
4. Handle errors gracefully

Test queries your agent must handle:
  "What is the total salary of all employees in the Engineering department?"
  "Find the budget of the Smart Task Agent project and calculate 15% of it"
  "Which department has the highest budget? Who leads it?"

Requirements:
1. Build a query_database tool that searches sample_db.json
2. Reuse calculator tool from previous files
3. Implement planning phase (LLM generates JSON plan)
4. Implement execution phase (run each step)
5. Print the plan and each step's result

STRETCH GOAL:
Add re-planning: if query_database returns no results, re-plan with a different query.

=============================================================================
HINTS (read ONE AT A TIME, only if stuck):
=============================================================================

HINT 1: The query_database tool should accept a table name and a search field/value.
         Example: query_database("employees", "department", "Engineering")
         Returns: matching rows as JSON string

HINT 2: For the planning prompt, tell the LLM about your tools AND the database schema:
         "query_database searches sample_db.json which has tables:
          employees (id, name, role, department, salary),
          projects (id, name, status, budget, lead),
          departments (name, head, headcount, budget)"

HINT 3: The execution loop pattern:
         plan = generate_plan(query)
         results = {}
         for step in plan:
             if step.tool == "query_database":
                 results[step.num] = query_database(step.input)
             elif step.tool == "calculator":
                 results[step.num] = calculator(step.input)
             elif step.tool == "reason":
                 results[step.num] = call_llm(step.input + context)

=============================================================================
STARTER CODE (fill in the blanks):
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


# ---- TOOL 1: Calculator (from Day 1) ----
def calculator(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"


# ---- TOOL 2: Query Database (YOU BUILD THIS) ----
def query_database(table: str, field: str = None, value: str = None) -> str:
    """
    Search sample_db.json.
    - table: which table to search ("employees", "projects", "departments")
    - field: which field to filter by (optional)
    - value: what value to match (optional)
    
    Returns: matching rows as JSON string
    
    Examples:
        query_database("employees", "department", "Engineering")
        query_database("projects", "status", "active")
        query_database("departments")  # returns all departments
    """
    # TODO: Implement this function
    # 1. Load sample_db.json
    # 2. Get the requested table
    # 3. If field and value provided, filter rows
    # 4. Return results as JSON string
    pass


# ---- LLM CALL ----
def call_llm(prompt: str) -> str:
    """Simple text generation."""
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
    }
    response = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, json=body)
    if response.status_code != 200:
        raise Exception(f"API error {response.status_code}: {response.text}")
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


# ---- PLANNING PHASE (YOU BUILD THIS) ----
def generate_plan(query: str) -> list:
    """
    Ask the LLM to create a plan for answering the query.
    The plan should be a JSON array of steps.
    """
    # TODO: Write a planning prompt that tells the LLM:
    # - What tools are available (calculator, query_database)
    # - What the database schema looks like
    # - To respond with a JSON array of steps
    # - Each step: {"step": N, "tool": "...", "input": "...", "purpose": "..."}
    pass


# ---- EXECUTION PHASE (YOU BUILD THIS) ----
def execute_plan(query: str, plan: list) -> str:
    """
    Execute each step of the plan and return the final answer.
    """
    # TODO: Loop through plan steps
    # - If tool is "query_database": parse input and call query_database()
    # - If tool is "calculator": call calculator()
    # - If tool is "reason": call call_llm() with context from previous steps
    # - Store results in a dict
    # - After all steps: generate final answer using call_llm()
    pass


# ---- MAIN AGENT ----
def run_agent(query: str) -> str:
    """Plan → Execute → Answer"""
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    # Phase 1: Plan
    plan = generate_plan(query)
    if not plan:
        return "Could not generate plan."
    
    print("\nPlan:")
    for step in plan:
        print(f"  Step {step.get('step', '?')}: {step.get('tool', '?')} — {step.get('purpose', '')}")
    
    # Phase 2: Execute
    answer = execute_plan(query, plan)
    
    print(f"\n✓ Answer: {answer[:300]}")
    return answer


# ---- TEST ----
if __name__ == "__main__":
    # Test 1: Database + Calculator
    run_agent("What is the total salary of all employees in the Engineering department?")
    
    print("\n")
    
    # Test 2: Database + Calculator
    run_agent("Find the budget of the Smart Task Agent project and calculate 15% of it")
    
    print("\n")
    
    # Test 3: Database + Reasoning
    run_agent("Which department has the highest budget? Who leads it?")
