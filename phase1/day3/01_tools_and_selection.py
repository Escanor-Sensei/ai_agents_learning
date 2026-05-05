"""
=============================================================================
DAY 3 - FILE 01: TOOLS & DYNAMIC SELECTION
=============================================================================

CONCEPT:
- Tools are functions the agent can call to interact with the real world.
- Each tool needs a name, description (docstring), and input schema.
- The LLM picks tools based on their descriptions — descriptions ARE the API.
- More tools = harder selection. The agent should pick the MINIMUM needed.
- Bad descriptions → wrong tool selected → wrong answer.

ANALOGY FOR .NET DEVS:
- Tools are like dependency-injected services.
- The LLM is the controller that picks which service to call.
- Tool descriptions = Swagger/OpenAPI documentation.
=============================================================================
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from _tools import ALL_TOOLS, BASIC_TOOLS, test_query

load_dotenv()

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))


# =========================
# STEP 1: Show available tools
# =========================

print("=" * 60)
print("AVAILABLE TOOLS")
print("=" * 60)

for t in ALL_TOOLS:
    print(f"  {t.name:20s} → {t.description[:70]}")


# =========================
# STEP 2: Agent with all 7 tools
# =========================

agent = create_react_agent(model=llm, tools=ALL_TOOLS)

print("\n\n" + "=" * 60)
print("SINGLE-TOOL QUERIES (agent should pick exactly one)")
print("=" * 60)

test_query(agent, "Math only", "What is 999 * 42?")
test_query(agent, "Search only", "Tell me about Python programming language")
test_query(agent, "Time only", "What's the current date?")


print("\n\n" + "=" * 60)
print("MULTI-TOOL QUERIES (agent chains tools)")
print("=" * 60)

test_query(agent, "Read + Summarize", "Read the file notes.txt and summarize its contents")
test_query(agent, "Search + Calculate", "Search for the world population and calculate 1% of 8.1 billion")


print("\n\n" + "=" * 60)
print("AMBIGUOUS QUERIES (tool selection is uncertain)")
print("=" * 60)

test_query(agent, "Summarize vs Search", "Give me a brief overview of machine learning")
test_query(agent, "Read vs Search", "Find information about the project budget")


print("""
=============================================================================
KEY OBSERVATIONS
=============================================================================

1. SINGLE-TOOL QUERIES → Agent picks the right tool from 7 options
2. MULTI-TOOL QUERIES → Agent chains: call tool 1 → observe → call tool 2
3. AMBIGUOUS QUERIES → Selection depends on description quality
4. The agent NEVER calls all tools — it picks the minimum needed

=============================================================================
DEEP THEORY: Tool Descriptions, Schemas & Selection
=============================================================================

1. TOOL DESCRIPTIONS ARE THE API
   The LLM only sees: name + description + parameter schema.
   It NEVER sees your Python code. The description IS the interface.
   Bad description → wrong tool selected → wrong answer.
   
   Example of BAD vs GOOD:
     BAD:  "process(data)" — process how? what data?
     GOOD: "Calculate a math expression. Input: Python expression like '2+3'"

2. JSON SCHEMA GENERATION
   The @tool decorator auto-generates JSON schema from type hints:
     @tool
     def calc(expression: str) -> str:  →  {"type": "object", "properties":
                                              {"expression": {"type": "string"}}}
   The LLM uses this to know what arguments to pass.

3. RAW TOOL REGISTRY (What the Framework Hides)
   Under the hood, tools are stored in a registry dict:
     TOOL_REGISTRY = {
         "calculator": {"function": calc_fn, "schema": {...}},
         "search_web": {"function": search_fn, "schema": {...}},
     }
   When the LLM returns a functionCall, the framework:
     1. Looks up the name in the registry
     2. Validates arguments against the schema
     3. Calls the function
     4. Returns result as a functionResponse

4. DYNAMIC SELECTION STRATEGY
   With many tools, the LLM may pick wrong. Strategies:
   - Group related tools (file_read + file_write in same category)
   - Use very specific descriptions (avoid overlap)
   - Limit to 5-10 tools per agent (more → worse accuracy)
   - For 50+ tools: use a "router" agent that picks a sub-agent

=============================================================================
""")
