"""
=============================================================================
DAY 1 - FILE 01: THE PROMPT (simplest possible LLM usage)
=============================================================================

CONCEPT (5 lines):
- A "prompt" is a single LLM call. You send text in, you get text out.
- There is NO logic, NO looping, NO decision-making.
- The developer controls everything: what goes in, what comes out.
- This is what 90% of "AI apps" actually are — glorified prompt calls.
- Think of it like calling a REST API: request -> response. Done.

ANALOGY FOR .NET DEVS:
- This is like calling HttpClient.PostAsync() once. 
- You send a request body, you get a response. No retry, no logic.
=============================================================================
"""

# ---- Python basics you need to know ----
# `import` = `using` in C#
# `from X import Y` = `using Y = X.Y` or `using static X.Y`
# No semicolons. Indentation matters (like YAML).
# `f"Hello {name}"` = $"Hello {name}" in C#

import os
from dotenv import load_dotenv  # Reads .env file into environment variables
from langchain_google_genai import ChatGoogleGenerativeAI

# load_dotenv() reads your .env file and sets GOOGLE_API_KEY as an env variable
# Same idea as IConfiguration in .NET, but simpler
load_dotenv()

# Create the LLM instance
# This is like creating an HttpClient configured to talk to Gemini
llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))

# --- THE PROMPT: One call. That's it. ---
response = llm.invoke("What is an AI agent in one sentence?")

print("=" * 60)
print("PROMPT RESPONSE:")
print("=" * 60)
print(response.content)
print("=" * 60)

# KEY OBSERVATION:
# - We sent ONE message
# - We got ONE response  
# - No tools, no memory, no decisions
# - The LLM cannot DO anything — it can only TALK
#
# This is NOT an agent. This is a fancy autocomplete.
