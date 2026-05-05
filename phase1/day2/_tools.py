"""
Shared tools and helpers for Day 2.
Import these instead of re-defining tools in every file.
"""

import os
import json
from datetime import datetime
from langchain_core.tools import tool


# =========================
# TOOLS
# =========================

@tool
def calculator(expression: str) -> str:
    """Calculate a math expression. Input: a valid Python expression like '2 + 3 * 4'."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"


@tool
def get_word_length(word: str) -> str:
    """Count the number of characters in a word or phrase. Returns the character count."""
    return str(len(word))


@tool
def search_web(query: str) -> str:
    """Search the web for information. Input: a search query string."""
    SEARCH_DB = {
        "python": "Python is a high-level programming language. Latest version: 3.12.",
        "langchain": "LangChain is a framework for building LLM applications.",
        "population": "World population: approximately 8.1 billion as of 2024.",
    }
    for key, val in SEARCH_DB.items():
        if key in query.lower():
            return val
    return f"No results for: {query}"


@tool
def read_file(file_path: str) -> str:
    """Read a text file's contents. Input: a filename like 'notes.txt'."""
    try:
        safe_path = os.path.basename(file_path)
        full_path = os.path.join(os.path.dirname(__file__), safe_path)
        if not os.path.exists(full_path):
            return f"Error: File '{safe_path}' not found."
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()[:2000]
    except Exception as e:
        return f"Error: {e}"


@tool
def get_current_time(format: str = "full") -> str:
    """Get current date/time. Input: 'full', 'date', or 'time'."""
    now = datetime.now()
    if format == "date":
        return now.strftime("%Y-%m-%d")
    elif format == "time":
        return now.strftime("%H:%M:%S")
    return now.strftime("%Y-%m-%d %H:%M:%S")


ALL_TOOLS = [calculator, get_word_length, search_web, read_file, get_current_time]


# =========================
# HELPERS
# =========================

def trace_messages(result):
    """Print a clean trace of every message in an agent result."""
    for i, msg in enumerate(result["messages"]):
        role = msg.__class__.__name__
        print(f"\n  Message {i} [{role}]:")

        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"    → TOOL CALL: {tc['name']}({tc['args']})")

        if hasattr(msg, "content") and msg.content:
            content = str(msg.content)[:200]
            print(f"    → Content: {content}")

        if hasattr(msg, "name") and msg.name:
            print(f"    → Tool name: {msg.name}")


def count_calls(result):
    """Count LLM calls and tool calls in an agent result."""
    llm_calls = sum(1 for m in result["messages"] if "AIMessage" in m.__class__.__name__)
    tool_calls = sum(1 for m in result["messages"] if "ToolMessage" in m.__class__.__name__)
    return llm_calls, tool_calls


def get_final_answer(result):
    """Extract the final text answer from an agent result."""
    for msg in reversed(result["messages"]):
        if "AIMessage" in msg.__class__.__name__ and hasattr(msg, "content") and msg.content:
            return str(msg.content)[:300]
    return "(no answer found)"
