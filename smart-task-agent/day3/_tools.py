"""
Shared tools and helpers for Day 3.
Import these instead of re-defining tools in every file.
"""

import os
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


SEARCH_DATABASE = {
    "python": "Python is a high-level programming language created by Guido van Rossum in 1991. Latest version: 3.12.",
    "langchain": "LangChain is a framework for building LLM applications. Created by Harrison Chase in 2022.",
    "react pattern": "ReAct (Reasoning + Acting) is an agent pattern from Yao et al. 2022.",
    "gemini": "Gemini is Google's multimodal AI model family.",
    "machine learning": "Machine learning is a subset of AI where systems learn from data.",
    "capital of france": "The capital of France is Paris, with a population of about 2.1 million.",
    "population": "World population: approximately 8.1 billion as of 2024.",
    "weather": "Current weather simulation: 72°F (22°C), partly cloudy.",
}


@tool
def search_web(query: str) -> str:
    """Search the web for information about a topic. Input: a search query string."""
    query_lower = query.lower()
    for key, value in SEARCH_DATABASE.items():
        if key in query_lower:
            return value
    return f"No results found for: '{query}'"


@tool
def read_file(file_path: str) -> str:
    """Read the contents of a text file. Input: a filename like 'notes.txt'."""
    try:
        safe_path = os.path.basename(file_path)
        full_path = os.path.join(os.path.dirname(__file__), safe_path)
        if not os.path.exists(full_path):
            return f"Error: File '{safe_path}' not found."
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content[:2000] + ("\n... (truncated)" if len(content) > 2000 else "")
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def write_file(file_path: str, content: str) -> str:
    """Write text content to a local file. Input: file_path, content. Creates or overwrites."""
    try:
        safe_path = os.path.basename(file_path)
        full_path = os.path.join(os.path.dirname(__file__), "output_" + safe_path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to output_{safe_path}"
    except Exception as e:
        return f"Error writing file: {e}"


@tool
def get_current_time(format: str = "full") -> str:
    """Get the current date and time. Input: 'full', 'date', or 'time'."""
    now = datetime.now()
    if format == "date":
        return now.strftime("%Y-%m-%d")
    elif format == "time":
        return now.strftime("%H:%M:%S")
    return now.strftime("%Y-%m-%d %H:%M:%S")


@tool
def summarize_text(text: str) -> str:
    """Summarize a long piece of text into a brief summary. Input: the text to summarize."""
    words = text.split()
    if len(words) <= 20:
        return text
    return " ".join(words[:20]) + "... (summary: " + str(len(words)) + " words total)"


ALL_TOOLS = [calculator, get_word_length, search_web, read_file, write_file, get_current_time, summarize_text]
BASIC_TOOLS = [calculator, get_word_length, search_web, read_file, get_current_time]


# =========================
# HELPERS
# =========================

def test_query(agent, label: str, query: str):
    """Run a query, print tools used and final answer."""
    print(f"\n{'='*60}")
    print(f"TEST: {label}")
    print(f"Query: {query}")
    print(f"{'='*60}")

    result = agent.invoke({"messages": [("human", query)]})

    tools_used = []
    final_answer = ""

    for msg in result["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tools_used.append(tc["name"])
                print(f"  → Tool: {tc['name']}({str(tc['args'])[:80]})")
        elif hasattr(msg, "content") and msg.content and "AIMessage" in msg.__class__.__name__:
            final_answer = str(msg.content)[:200]

    print(f"  Tools used: {tools_used}")
    print(f"  Answer: {final_answer}")
    return tools_used
