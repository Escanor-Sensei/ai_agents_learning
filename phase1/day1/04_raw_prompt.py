"""
=============================================================================
DAY 1 - FILE 04: RAW PROMPT (No framework — just HTTP)
=============================================================================

UNDER THE HOOD:
When you call `llm.invoke("...")` in LangChain, here's what ACTUALLY happens:
1. Your text gets wrapped in a JSON body
2. An HTTP POST is sent to Gemini's REST API
3. The JSON response is parsed
4. The text is extracted and returned

That's it. LangChain's `invoke()` is a glorified HTTP call.
Let's prove it.
=============================================================================
"""

import os
import json
from dotenv import load_dotenv

# `requests` is Python's HttpClient equivalent
# If not installed: pip install requests
try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system("pip install requests")
    import requests

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL")

# This is the actual Gemini REST endpoint.
# LangChain calls this exact URL behind the scenes.
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

# The request body — this is what LangChain constructs for you
request_body = {
    "contents": [
        {
            "role": "user",
            "parts": [
                {"text": "What is an AI agent in one sentence?"}
            ]
        }
    ]
}

print("=" * 60)
print("RAW PROMPT (no framework)")
print("=" * 60)

# --- THE ACTUAL HTTP CALL ---
# This is ALL that LangChain's invoke() does (plus error handling)
response = requests.post(
    GEMINI_URL,
    headers={"Content-Type": "application/json"},
    json=request_body
)

# Parse the response
data = response.json()

# Check for errors first
if "error" in data:
    print(f"\n❌ API Error: {data['error']}")
    print("\nFull response:")
    print(json.dumps(data, indent=2))
    exit(1)

# Extract the text — this is what LangChain's response.content gives you
if "candidates" in data and len(data["candidates"]) > 0:
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    print(f"\nResponse:\n{text}")
else:
    print(f"\n❌ Unexpected response structure:")
    print(json.dumps(data, indent=2))
    exit(1)

print("=" * 60)

# --- COMPARE ---
# LangChain version (from 01_prompt.py):
#   response = llm.invoke("What is an AI agent in one sentence?")
#   print(response.content)
#
# Raw version (this file):
#   response = requests.post(URL, json=body)
#   text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
#
# LangChain saves you ~10 lines and handles errors.
# But CONCEPTUALLY, it's the same thing: HTTP POST -> parse JSON.
#
# LESSON: There is no magic. It's just HTTP.

print("\n--- Full raw JSON response (so you can see the structure) ---")
print(json.dumps(data, indent=2)[:2000])  # Truncate to keep output readable
