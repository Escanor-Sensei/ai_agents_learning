"""
=============================================================================
DAY 1 - FILE 02: THE WORKFLOW (developer-controlled chain of steps)
=============================================================================

CONCEPT (5 lines):
- A workflow is a CHAIN of LLM calls where the DEVELOPER controls the order.
- Step A's output feeds into Step B's input. Always in the same order.
- The LLM never decides what to do next — YOU hardcode the sequence.
- Think: pipeline. Like middleware in ASP.NET: Request -> Auth -> Route -> Response.
- More powerful than a single prompt, but still NOT an agent.

KEY DIFFERENCE FROM AGENT:
- Workflow: Developer decides flow (if/else, fixed sequence)
- Agent: LLM decides flow (dynamic, unpredictable)
=============================================================================
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# In LangChain, a "chain" = prompt template + LLM + output parser piped together
# The `|` operator is LangChain's way of chaining (like Unix pipes)

load_dotenv()

llm = ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"))

# --- STEP 1: Research ---
# A prompt template is like a string.Format() with named placeholders
research_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a researcher. Given a topic, produce 3 key facts. Be concise. Output ONLY the 3 facts as bullet points."),
    ("human", "Topic: {topic}")
])

# --- STEP 2: Analyze ---
analyze_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an analyst. Given research notes, extract the single most important insight. One sentence only."),
    ("human", "Research notes:\n{research}")
])

# --- STEP 3: Write ---
write_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a writer. Given an insight, write a compelling one-paragraph summary (3-4 sentences)."),
    ("human", "Key insight: {insight}")
])

# --- THE WORKFLOW: Fixed sequence, developer-controlled ---
print("=" * 60)
print("WORKFLOW: Research -> Analyze -> Write")
print("=" * 60)

# Get topic from user
topic = input("Enter a topic to research: ")

# Step 1: Research
print("\n[STEP 1] Researching...")
research_chain = research_prompt | llm
research_result = research_chain.invoke({"topic": topic})
print(f"Research output:\n{research_result.content}")

# Step 2: Analyze (feeds research output into analyze prompt)
print("\n[STEP 2] Analyzing...")
analyze_chain = analyze_prompt | llm
analysis_result = analyze_chain.invoke({"research": research_result.content})
print(f"Analysis output:\n{analysis_result.content}")

# Step 3: Write (feeds analysis into write prompt)
print("\n[STEP 3] Writing...")
write_chain = write_prompt | llm
write_result = write_chain.invoke({"insight": analysis_result.content})
print(f"\nFinal output:\n{write_result.content}")

print("=" * 60)

# KEY OBSERVATION:
# - The order is ALWAYS Research -> Analyze -> Write
# - The LLM never chose to skip a step or go back
# - The LLM never decided "I need to research more" 
# - If Step 2 produces garbage, Step 3 runs anyway
# - This is a PIPELINE, not an agent
#
# WHAT'S MISSING FOR AN AGENT:
# 1. The LLM should DECIDE what to do next
# 2. The LLM should be able to LOOP (retry, go back)
# 3. The LLM should have TOOLS (not just text generation)
