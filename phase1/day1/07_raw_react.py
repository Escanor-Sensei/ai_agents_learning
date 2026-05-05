"""
=============================================================================
DAY 1 - FILE 07: RAW ReAct AGENT with NATIVE FUNCTION CALLING
=============================================================================

File 05 used text parsing (THOUGHT/ACTION/FINAL_ANSWER format).
That's fragile — the LLM often doesn't follow the format exactly.

Modern LLMs (Gemini, GPT-4, Claude) support NATIVE FUNCTION CALLING:
- You send tool definitions as JSON schemas
- The LLM returns structured function calls (not free text)
- Much more reliable than text parsing

This is what LangChain actually uses. Let's build it raw.
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
# STEP 1: Define tools as Python functions
# =========================
def calculator(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"


def get_word_length(word: str) -> str:
    return str(len(word))


TOOLS = {
    "calculator": calculator,
    "get_word_length": get_word_length,
}


# =========================
# STEP 2: Define tool SCHEMAS for the API
# =========================
# This is what LangChain generates from your @tool decorator + docstring.
# It's a JSON Schema that tells the LLM what the tool does and what inputs it takes.

TOOL_DECLARATIONS = [
    {
        "name": "calculator",
        "description": "Calculate a math expression. Input should be a valid Python math expression like '2 + 3 * 4'. Returns the numeric result.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The math expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "get_word_length",
        "description": "Count the number of characters in a word or phrase. Returns the character count.",
        "parameters": {
            "type": "object",
            "properties": {
                "word": {
                    "type": "string",
                    "description": "The word or phrase to count characters in"
                }
            },
            "required": ["word"]
        }
    }
]


# =========================
# STEP 3: Call Gemini WITH tool declarations
# =========================
def call_gemini_with_tools(contents: list) -> dict:
    """
    Call Gemini with function calling enabled.
    The API response will either contain:
    - A text response (final answer)
    - A functionCall (the LLM wants to use a tool)
    """
    body = {
        "contents": contents,
        "tools": [{"functionDeclarations": TOOL_DECLARATIONS}],
        # This system instruction replaces the big SYSTEM_PROMPT from file 05
        "systemInstruction": {
            "parts": [{"text": "You are a helpful assistant. Use the provided tools when needed to answer questions accurately. Think step by step."}]
        }
    }

    response = requests.post(
        GEMINI_URL,
        headers={"Content-Type": "application/json"},
        json=body
    )

    if response.status_code != 200:
        raise Exception(f"API error {response.status_code}: {response.text}")

    return response.json()


# =========================
# STEP 4: THE AGENT LOOP (with native function calling)
# =========================
def run_agent(query: str, max_iterations: int = 10) -> str:
    """
    Same loop as file 05, but using native function calling instead of text parsing.
    
    THE LOOP:
    1. Send messages to Gemini (with tool schemas)
    2. Gemini responds with either text or a functionCall
    3. If functionCall: execute tool, add result to messages, go to 1
    4. If text: that's the final answer
    """

    # Start with the user's query
    contents = [
        {"role": "user", "parts": [{"text": query}]}
    ]

    print(f"\n{'='*60}")
    print(f"RAW AGENT LOOP (native function calling)")
    print(f"Query: {query}")
    print(f"{'='*60}")

    for iteration in range(max_iterations):
        print(f"\n--- Iteration {iteration + 1} ---")

        # STEP 4a: Call Gemini
        response_data = call_gemini_with_tools(contents)

        # STEP 4b: Extract the response
        candidate = response_data["candidates"][0]
        parts = candidate["content"]["parts"]

        # Add the model's response to our conversation history
        contents.append({"role": "model", "parts": parts})

        # STEP 4c: Check what the LLM wants to do
        for part in parts:
            if "functionCall" in part:
                # LLM wants to call a tool!
                func_call = part["functionCall"]
                tool_name = func_call["name"]
                tool_args = func_call.get("args", {})

                print(f"→ Function call: {tool_name}({json.dumps(tool_args)})")

                # STEP 4d: Execute the tool
                if tool_name in TOOLS:
                    # Get the first argument value (tools have single args here)
                    arg_value = list(tool_args.values())[0] if tool_args else ""
                    tool_result = TOOLS[tool_name](arg_value)
                    print(f"→ Result: {tool_result}")
                else:
                    tool_result = f"Error: Unknown tool '{tool_name}'"

                # STEP 4e: Send the tool result back to Gemini
                # This is the "Observation" step in ReAct
                contents.append({
                    "role": "user",
                    "parts": [{
                        "functionResponse": {
                            "name": tool_name,
                            "response": {"result": tool_result}
                        }
                    }]
                })

            elif "text" in part:
                # LLM is giving a text response (could be final answer)
                text = part["text"]
                print(f"→ Text: {text}")

        # Check if the last response was purely text (no function calls)
        # That means the LLM is done — it's the final answer
        has_function_call = any("functionCall" in p for p in parts)
        if not has_function_call:
            # Extract final text
            final_text = " ".join(p.get("text", "") for p in parts if "text" in p)
            print(f"\n✓ FINAL ANSWER: {final_text}")
            return final_text

    return "Agent exceeded max iterations."


# =========================
# STEP 5: TEST & COMPARE
# =========================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TEST 1: Single tool (calculator)")
    print("=" * 60)
    answer1 = run_agent("What is 15 * 23 + 7?")

    print("\n\n" + "=" * 60)
    print("TEST 2: Two tools (word length + calculator)")
    print("=" * 60)
    answer2 = run_agent(
        "How many characters are in the word 'artificial' and what is that number times 5?"
    )

    # =========================
    # COMPARISON: Three approaches
    # =========================
    print("\n\n" + "=" * 60)
    print("COMPARISON OF ALL THREE APPROACHES")
    print("=" * 60)
    print("""
    ┌─────────────────────┬──────────────────────┬─────────────────────────┐
    │ File 05: Raw Text   │ File 07: Raw Native  │ File 06: LangChain     │
    │ Parsing             │ Function Calling     │ create_react_agent     │
    ├─────────────────────┼──────────────────────┼─────────────────────────┤
    │ Text prompt with    │ JSON tool schemas    │ @tool decorator →      │
    │ THOUGHT/ACTION      │ sent to API          │ auto-generates schemas │
    │ format              │                      │                        │
    ├─────────────────────┼──────────────────────┼─────────────────────────┤
    │ String parsing to   │ Structured JSON      │ LangChain parses       │
    │ extract tool calls  │ response (reliable)  │ response automatically │
    ├─────────────────────┼──────────────────────┼─────────────────────────┤
    │ Fragile — LLM may   │ Reliable — API       │ Most reliable — has    │
    │ not follow format   │ enforces structure   │ error recovery too     │
    ├─────────────────────┼──────────────────────┼─────────────────────────┤
    │ ~80 lines of loop   │ ~50 lines of loop    │ ~5 lines               │
    │ code                │ code                 │ (create_react_agent)   │
    ├─────────────────────┼──────────────────────┼─────────────────────────┤
    │ SAME CORE LOGIC     │ SAME CORE LOGIC      │ SAME CORE LOGIC        │
    │ while loop + tools  │ while loop + tools   │ while loop + tools     │
    └─────────────────────┴──────────────────────┴─────────────────────────┘
    
    THE POINT: All three are the SAME while loop.
    The only difference is how tool calls are communicated (text vs JSON)
    and how much boilerplate the framework handles for you.
    """)
