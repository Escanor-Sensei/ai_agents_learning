"""
Tool Registry — tools/__init__.py

This is the single source of truth for all registered tools.

.NET analogy:
  This file = Program.cs / Startup.cs where you call builder.Services.Add...()
  Importing from here = resolving services from IServiceProvider

To add a new tool:
  1. Create tools/your_tool.py with a @tool decorated function
  2. Import it here
  3. Add it to the `all_tools` list — that's it
"""

from tools.calculator import calculator
from tools.web_search import web_search
from tools.db_query import db_query

# The agent will only know about tools in this list.
# Order doesn't matter — the LLM picks based on tool descriptions.
all_tools = [calculator, web_search, db_query]
