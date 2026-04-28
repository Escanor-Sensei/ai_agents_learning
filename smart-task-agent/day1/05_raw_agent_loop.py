"""
=============================================================================
DAY 1 - FILE 05: RAW AGENT LOOP (No framework — the truth about agents)
=============================================================================

THIS IS THE MOST IMPORTANT FILE OF DAY 1.

Here's the secret: An agent is just a WHILE LOOP.

    while not done:
        response = call_llm(prompt + history)
        if response says "use a tool":
            result = call_tool(response.tool_name, response.tool_input)
            history.append(result)
        elif response says "final answer":
            done = True

That's it. LangChain's create_react_agent, AgentExecutor, ReAct —
all of it boils down to this while loop.

Let's build it from scratch with raw HTTP calls.
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
# STEP 1: Define our tools
# =========================
# A tool is just a Python function. Nothing magical.
# We also need a DESCRIPTION so the LLM knows when to use it.

def calculator(expression: str) -> str:
    """Calculate a math expression."""
    try:
        result = eval(expression)  # Don't use eval in production!
        return str(result)
    except Exception as e:
        return f"Error: {e}"


def get_word_length(word: str) -> str:
    """Count characters in a word."""
    return str(len(word))


# Tool registry — maps name to function
TOOLS = {
    "calculator": calculator,
    "get_word_length": get_word_length,
}

# Tool descriptions — this is what the LLM reads to decide which tool to use
TOOL_DESCRIPTIONS = """
Available tools:

1. calculator
   Description: Calculate a math expression. Input should be a valid math expression like '2 + 3 * 4'
   Input: a math expression string

2. get_word_length
   Description: Count the number of characters in a word. Input should be a single word.
   Input: a single word string
"""


# ==================================
# STEP 2: The System Prompt (ReAct)
# ==================================
# This is the EXACT pattern that LangChain uses internally.
# The ReAct format tells the LLM to:
#   1. Think about what to do
#   2. Choose an action (tool call) OR give a final answer
#   3. Observe the tool result
#   4. Repeat

SYSTEM_PROMPT = f"""You are a helpful AI assistant with access to tools.

{TOOL_DESCRIPTIONS}

To use a tool, respond in EXACTLY this format (no extra text):
THOUGHT: <your reasoning about what to do>
ACTION: <tool_name>
ACTION_INPUT: <input to the tool>

When you have the final answer, respond in EXACTLY this format:
THOUGHT: <your reasoning>
FINAL_ANSWER: <your answer to the user>

IMPORTANT RULES:
- Always start with THOUGHT
- Use only ONE tool per turn
- After seeing a tool result, you may use another tool or give FINAL_ANSWER
- Never make up tool results — always call the tool
"""


# =================================
# STEP 3: Call Gemini (raw HTTP)
# =================================
def call_gemini(messages: list) -> str:
    """Send messages to Gemini and get response text."""
    # Convert our messages to Gemini's format
    contents = []
    for msg in messages:
        contents.append({
            "role": msg["role"],
            "parts": [{"text": msg["content"]}]
        })

    body = {"contents": contents}
    response = requests.post(
        GEMINI_URL,
        headers={"Content-Type": "application/json"},
        json=body
    )

    if response.status_code != 200:
        raise Exception(f"Gemini API error: {response.status_code}\n{response.text}")

    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


# ==================================
# STEP 4: Parse the LLM's response
# ==================================
def parse_response(text: str):
    """
    Parse the LLM's response to extract thought, action, and input.
    Returns: ("tool_call", tool_name, tool_input) or ("final_answer", answer, None)
    """
    lines = text.strip().split("\n")

    thought = ""
    action = None
    action_input = None
    final_answer = None

    for line in lines:
        line = line.strip()
        if line.startswith("THOUGHT:"):
            thought = line[len("THOUGHT:"):].strip()
        elif line.startswith("ACTION:"):
            action = line[len("ACTION:"):].strip()
        elif line.startswith("ACTION_INPUT:"):
            action_input = line[len("ACTION_INPUT:"):].strip()
        elif line.startswith("FINAL_ANSWER:"):
            final_answer = line[len("FINAL_ANSWER:"):].strip()

    if final_answer:
        return ("final_answer", final_answer, thought)
    elif action and action_input is not None:
        return ("tool_call", action, action_input)
    else:
        # LLM didn't follow format — treat as final answer
        return ("final_answer", text, thought)


# ==================================
# STEP 5: THE AGENT LOOP
# ==================================
# THIS IS THE CORE OF EVERY AGENT IN EXISTENCE.
# Everything else is just fancy wrapping around this loop.

def run_agent(query: str, max_iterations: int = 5) -> str:
    """
    Run the agent loop:
    1. Send query + history to LLM
    2. LLM responds with THOUGHT + ACTION or FINAL_ANSWER
    3. If ACTION: execute tool, add result to history, go to 1
    4. If FINAL_ANSWER: return it
    """
    # Message history — this is the agent's "working memory"
    messages = [
        {"role": "user", "content": SYSTEM_PROMPT + "\n\nUser query: " + query}
    ]

    print(f"\n{'='*60}")
    print(f"AGENT LOOP START")
    print(f"Query: {query}")
    print(f"{'='*60}")

    for iteration in range(max_iterations):
        print(f"\n--- Iteration {iteration + 1} ---")

        # STEP 5a: Call the LLM
        llm_response = call_gemini(messages)
        print(f"LLM says:\n{llm_response}")

        # STEP 5b: Parse what the LLM wants to do
        result_type, value, extra = parse_response(llm_response)

        if result_type == "final_answer":
            print(f"\n✓ FINAL ANSWER: {value}")
            return value

        elif result_type == "tool_call":
            tool_name = value
            tool_input = extra if extra else ""

            # Wait — parse_response returns (type, action, action_input)
            # Let me re-check the parsing...
            # Actually for tool_call: ("tool_call", action, action_input)
            tool_input = extra  # This is action_input from parse

            # Oops, parse_response returns thought in extra for final_answer
            # but action_input in value for tool_call... let me fix the unpack
            tool_name = value
            # Re-parse to get action_input properly
            lines = llm_response.strip().split("\n")
            for line in lines:
                if line.strip().startswith("ACTION_INPUT:"):
                    tool_input = line.strip()[len("ACTION_INPUT:"):].strip()

            print(f"→ Tool: {tool_name}")
            print(f"→ Input: {tool_input}")

            # STEP 5c: Execute the tool
            if tool_name in TOOLS:
                tool_result = TOOLS[tool_name](tool_input)
                print(f"→ Result: {tool_result}")
            else:
                tool_result = f"Error: Unknown tool '{tool_name}'"
                print(f"→ ERROR: {tool_result}")

            # STEP 5d: Add the exchange to history so the LLM sees it
            messages.append({"role": "model", "content": llm_response})
            messages.append({
                "role": "user",
                "content": f"OBSERVATION: {tool_result}\n\nNow continue. Use another tool or provide FINAL_ANSWER."
            })

    return "Agent exceeded max iterations without reaching a final answer."


# ==================================
# STEP 6: TEST IT
# ==================================
if __name__ == "__main__":
    # Test 1: Simple calculator
    answer1 = run_agent("What is 15 * 23 + 7?")
    print(f"\n{'='*60}")
    print(f"Answer: {answer1}")
    print(f"Expected: 352")
    print(f"{'='*60}")

    # Test 2: Two tools needed
    print("\n\n")
    answer2 = run_agent(
        "How many characters are in the word 'artificial' and what is that number times 5?"
    )
    print(f"\n{'='*60}")
    print(f"Answer: {answer2}")
    print(f"Expected: 10 characters, 10 * 5 = 50")
    print(f"{'='*60}")

    # ==================================
    # KEY TAKEAWAYS
    # ==================================
    # 
    # 1. The agent is a WHILE LOOP (lines 115-160)
    # 2. The "intelligence" is just the SYSTEM PROMPT telling the LLM the format
    # 3. Tool "selection" is just the LLM outputting a tool name as text
    # 4. The "memory" is just the message history list
    # 5. "Execution" is just calling a Python function by name from a dictionary
    #
    # LangChain's create_react_agent does EXACTLY this, but:
    # - Uses native function calling instead of text parsing (more reliable)
    # - Has better error handling
    # - Supports async, streaming, callbacks
    # - Handles edge cases (malformed output, tool errors)
    #
    # But the CORE LOGIC is identical to this file.
