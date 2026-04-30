"""
=============================================================================
DAY 2 - FILE 06: REFERENCE SOLUTION — Planning Agent
=============================================================================

⚠️  DO NOT READ THIS until you've attempted 04_task_build_planner.py yourself!
     Struggle is where learning happens.
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


# ---- TOOL 1: Calculator ----
def calculator(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"


# ---- TOOL 2: Query Database ----
def query_database(table: str, field: str = None, value: str = None) -> str:
    """Search sample_db.json for data."""
    db_path = os.path.join(os.path.dirname(__file__), "sample_db.json")
    
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            db = json.load(f)
    except FileNotFoundError:
        return "Error: Database file not found"
    except json.JSONDecodeError:
        return "Error: Invalid database format"
    
    # Get the table
    if table not in db:
        return f"Error: Table '{table}' not found. Available tables: {list(db.keys())}"
    
    rows = db[table]
    
    # Filter if field and value provided
    if field and value:
        filtered = [row for row in rows if str(row.get(field, "")).lower() == str(value).lower()]
        if not filtered:
            return f"No rows in '{table}' where {field} = '{value}'"
        return json.dumps(filtered, indent=2)
    
    # Return all rows if no filter
    return json.dumps(rows, indent=2)


TOOLS = {
    "calculator": calculator,
    "query_database": query_database,
}

DB_SCHEMA = """Database schema (sample_db.json):
- employees: id, name, role, department, salary
- projects: id, name, status, budget, lead
- departments: name, head, headcount, budget"""


# ---- LLM CALL ----
def call_llm(prompt: str) -> str:
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
    }
    response = requests.post(GEMINI_URL, headers={"Content-Type": "application/json"}, json=body)
    if response.status_code != 200:
        raise Exception(f"API error {response.status_code}: {response.text}")
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


# ---- PLANNING PHASE ----
def generate_plan(query: str, context: str = "") -> list:
    prompt = f"""You are a planning assistant. Create a step-by-step plan to answer the query.

Available tools:
- calculator: Calculate math expressions. Input: a Python math expression string.
- query_database: Query the database. Input should be JSON like: {{"table": "employees", "field": "department", "value": "Engineering"}} or {{"table": "employees"}} for all rows.

{DB_SCHEMA}

{f"Context from failed steps: {context}" if context else ""}

User query: {query}

Respond with ONLY a JSON array:
[
  {{"step": 1, "tool": "query_database", "input": {{"table": "employees", "field": "department", "value": "Engineering"}}, "purpose": "Get engineering employees"}},
  {{"step": 2, "tool": "calculator", "input": "95000 + 90000 + 92000", "purpose": "Sum salaries"}},
  {{"step": 3, "tool": "reason", "input": "Combine results from steps 1 and 2", "purpose": "Final answer"}}
]"""

    response = call_llm(prompt)
    
    try:
        start = response.find("[")
        end = response.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except json.JSONDecodeError:
        pass
    
    return []


# ---- EXECUTION PHASE ----
def execute_plan(query: str, plan: list, max_replans: int = 2) -> str:
    step_results = {}
    replans_used = 0
    
    i = 0
    while i < len(plan):
        step = plan[i]
        step_num = step.get("step", i + 1)
        tool_name = step.get("tool", "reason")
        step_input = step.get("input", "")
        purpose = step.get("purpose", "")
        
        print(f"\n  Step {step_num}: {tool_name} — {purpose}")
        
        if tool_name == "query_database":
            # Parse the input as dict for query_database
            if isinstance(step_input, dict):
                db_args = step_input
            elif isinstance(step_input, str):
                try:
                    db_args = json.loads(step_input)
                except json.JSONDecodeError:
                    db_args = {"table": step_input}
            else:
                db_args = {"table": str(step_input)}
            
            result = query_database(
                table=db_args.get("table", ""),
                field=db_args.get("field"),
                value=db_args.get("value")
            )
            
            if result.startswith("Error:") or result.startswith("No rows"):
                print(f"    ✗ {result}")
                if replans_used < max_replans:
                    replans_used += 1
                    context = f"Step {step_num} failed: {result}. Completed results: {json.dumps(step_results)}"
                    new_plan = generate_plan(query, context)
                    if new_plan:
                        plan = new_plan
                        step_results = {}
                        i = 0
                        print(f"    → Re-planned ({replans_used}/{max_replans})")
                        continue
            
            step_results[step_num] = result
            print(f"    ✓ Got {len(json.loads(result)) if result.startswith('[') else 1} results")
            
        elif tool_name == "calculator":
            # Substitute previous step results into the expression
            expression = str(step_input)
            for prev_num, prev_result in step_results.items():
                expression = expression.replace(f"step_{prev_num}", str(prev_result))
                expression = expression.replace(f"step {prev_num}", str(prev_result))
            
            # If expression references previous data, ask LLM to extract numbers
            if not any(c.isdigit() for c in expression):
                extract_prompt = f"Extract the numbers needed for this calculation from previous results.\nCalculation needed: {expression}\nPrevious results: {json.dumps(step_results)}\nRespond with ONLY the math expression (e.g., '95000 + 90000 + 92000')"
                expression = call_llm(extract_prompt).strip()
            
            result = calculator(expression)
            step_results[step_num] = result
            print(f"    ✓ {expression} = {result}")
            
        elif tool_name == "reason":
            reason_prompt = f"""Based on these results:
{json.dumps(step_results, indent=2)}

Task: {step_input}
Original query: {query}

Provide a clear answer."""
            
            result = call_llm(reason_prompt)
            step_results[step_num] = result
            print(f"    ✓ {result[:100]}")
        else:
            print(f"    ✗ Unknown tool: {tool_name}")
            step_results[step_num] = f"Error: Unknown tool '{tool_name}'"
        
        i += 1
    
    # Generate final answer
    final_prompt = f"""Based on this data:
{json.dumps(step_results, indent=2)}

Original query: {query}

Give a clear, concise final answer."""
    
    return call_llm(final_prompt)


# ---- MAIN AGENT ----
def run_agent(query: str) -> str:
    print(f"\n{'='*60}")
    print(f"PLANNING AGENT (with database tool)")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    # Phase 1: Plan
    print("\n--- Phase 1: PLANNING ---")
    plan = generate_plan(query)
    
    if not plan:
        print("  Could not generate plan.")
        return call_llm(query)
    
    for step in plan:
        print(f"  {step.get('step', '?')}. [{step.get('tool', '?')}] {step.get('purpose', '')}")
    
    # Phase 2: Execute
    print("\n--- Phase 2: EXECUTION ---")
    answer = execute_plan(query, plan)
    
    print(f"\n{'='*60}")
    print(f"✓ FINAL ANSWER: {answer[:300]}")
    print(f"{'='*60}")
    
    return answer


# ---- TEST ----
if __name__ == "__main__":
    # Test 1: Database + Calculator
    result1 = run_agent("What is the total salary of all employees in the Engineering department?")
    print(f"\nExpected: ~277000 (95000 + 90000 + 92000)")
    
    print("\n")
    
    # Test 2: Database + Calculator  
    result2 = run_agent("Find the budget of the Smart Task Agent project and calculate 15% of it")
    print(f"\nExpected: 7500 (50000 * 0.15)")
    
    print("\n")
    
    # Test 3: Database + Reasoning
    result3 = run_agent("Which department has the highest budget? Who leads it?")
    print(f"\nExpected: Engineering (500000), led by Alice Johnson")
