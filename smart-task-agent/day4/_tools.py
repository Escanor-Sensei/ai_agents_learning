"""
Shared tools and helpers for Day 4.
Import these instead of re-defining tools in every file.
"""

from langchain_core.tools import tool


# =========================
# TOOLS
# =========================

@tool
def calculator(expression: str) -> str:
    """Calculate a math expression. Input should be a valid Python math expression like '2 + 3 * 4'. Returns the numeric result."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error calculating '{expression}': {e}"


@tool
def get_word_length(word: str) -> str:
    """Count the number of characters in a word or phrase. Returns the character count."""
    return str(len(word))


ALL_TOOLS = [calculator, get_word_length]


# =========================
# HELPERS
# =========================

def trace_messages(result):
    """Print a clean trace of every message in an agent result."""
    for i, msg in enumerate(result["messages"]):
        role = msg.__class__.__name__
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"    [{role}] → Calls tool: {tc['name']}({tc['args']})")
        elif hasattr(msg, "content") and msg.content:
            content = str(msg.content)[:200]
            print(f"    [{role}] → {content}")


def count_calls(result):
    """Count LLM calls and tool calls in an agent result."""
    llm_calls = sum(1 for m in result["messages"] if "AIMessage" in m.__class__.__name__)
    tool_calls = sum(1 for m in result["messages"] if "ToolMessage" in m.__class__.__name__)
    return llm_calls, tool_calls
