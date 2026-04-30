"""
=============================================================================
DAY 3 - FILE 02: TOOL SCHEMAS — How LLMs See Your Tools
=============================================================================

CONCEPT:
- The LLM never sees your Python code — only the JSON schema.
- Schema = name + description + parameter types. That's the LLM's "API docs."
- Bad schema/description → LLM calls the wrong tool or passes wrong args.
- You can inspect schemas programmatically to debug tool selection issues.

ANALOGY FOR .NET DEVS:
- Tool schemas are like Swagger docs for your API endpoints.
- If your Swagger says "process data" with no details, clients can't use it.
=============================================================================
"""

import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from _tools import ALL_TOOLS, calculator, search_web

load_dotenv()

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))


# =========================
# STEP 1: Inspect tool schemas
# =========================

print("=" * 60)
print("TOOL SCHEMAS — What the LLM actually sees")
print("=" * 60)

for t in ALL_TOOLS:
    schema = {
        "name": t.name,
        "description": t.description,
        "parameters": t.args,
    }
    print(f"\n{json.dumps(schema, indent=2)}")


# =========================
# STEP 2: Experiment — vague vs specific descriptions
# =========================

print("\n\n" + "=" * 60)
print("EXPERIMENT: Vague vs Specific descriptions")
print("=" * 60)

# Vague tool
@tool
def process(data: str) -> str:
    """Process the data."""
    try:
        return str(eval(data))
    except:
        return data.upper()

# Specific tool (same function!)
@tool
def calculate_expression(expression: str) -> str:
    """Calculate a math expression. Input should be a valid Python math expression like '2 + 3 * 4'. Returns the numeric result."""
    try:
        return str(eval(expression))
    except:
        return expression.upper()

query = "What is 25 * 4?"

print(f"\nQuery: {query}")

# Test with vague tool
agent_vague = create_react_agent(model=llm, tools=[process])
result_vague = agent_vague.invoke({"messages": [("human", query)]})
vague_tools = [tc["name"] for msg in result_vague["messages"]
               if hasattr(msg, "tool_calls") and msg.tool_calls
               for tc in msg.tool_calls]
print(f"\n  Vague tool ('process'):    tools_used={vague_tools}, answer={result_vague['messages'][-1].content[:100]}")

# Test with specific tool
agent_specific = create_react_agent(model=llm, tools=[calculate_expression])
result_specific = agent_specific.invoke({"messages": [("human", query)]})
specific_tools = [tc["name"] for msg in result_specific["messages"]
                  if hasattr(msg, "tool_calls") and msg.tool_calls
                  for tc in msg.tool_calls]
print(f"  Specific tool ('calc...'):  tools_used={specific_tools}, answer={result_specific['messages'][-1].content[:100]}")


print("""
=============================================================================
KEY INSIGHT
=============================================================================

Same underlying function, but:
- Vague description → LLM may not use the tool at all
- Specific description → LLM confidently picks and uses it correctly

The DESCRIPTION is more important than the CODE.
Write tool descriptions like you'd write API documentation.

GOOD DESCRIPTION CHECKLIST:
  ✓ What does it do? (action verb)
  ✓ What input does it expect? (with an example)
  ✓ What does it return?
  ✗ Don't say "process" or "handle" — be specific

=============================================================================
""")
