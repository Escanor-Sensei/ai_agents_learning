"""
=============================================================================
DAY 4 - FILE 04: ERROR HANDLING (Making Agents Robust)
=============================================================================

CONCEPT (5 lines):
- Real agents face: tool exceptions, malformed LLM responses, API rate limits.
- Without error handling, a single bad tool result crashes the whole agent.
- Key patterns: try/except per tool, fallback parsing, max retries, timeouts.
- The agent should GRACEFULLY degrade, not crash. Return partial info if needed.
- This is the difference between a demo and a production system.

ANALOGY FOR .NET DEVS:
- Tool error handling = try/catch per service call + Polly retry policies.
- Malformed response = JSON deserialization failure + fallback.
- Rate limit = 429 Too Many Requests + exponential backoff.
=============================================================================
"""

import os
import json
import time
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
# ERROR PATTERN 1: Tool that throws exceptions
# =========================

def safe_calculator(expression: str) -> str:
    """Calculator with error handling."""
    try:
        # Prevent dangerous eval inputs
        allowed = set("0123456789+-*/.() ")
        if not all(c in allowed for c in expression):
            return f"Error: Invalid characters in expression. Only math operations allowed."
        result = eval(expression)
        return str(result)
    except ZeroDivisionError:
        return "Error: Division by zero."
    except SyntaxError:
        return f"Error: Invalid syntax in '{expression}'. Check parentheses and operators."
    except Exception as e:
        return f"Error: Calculation failed — {type(e).__name__}: {e}"


def unreliable_search(query: str) -> str:
    """Simulates a search that sometimes fails."""
    import random
    if random.random() < 0.3:  # 30% failure rate
        raise ConnectionError("Search service unavailable")
    return f"Search result for: {query}"


def safe_tool_call(tool_func, *args, max_retries: int = 2, **kwargs) -> str:
    """Wrapper that retries tool calls on failure."""
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            result = tool_func(*args, **kwargs)
            return result
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                print(f"    [retry] Tool failed (attempt {attempt+1}): {e}. Retrying...")
                time.sleep(0.5)  # Brief delay before retry
    
    return f"Error after {max_retries+1} attempts: {last_error}"


# =========================
# ERROR PATTERN 2: Malformed LLM response
# =========================

def robust_parse_response(response_data: dict) -> dict:
    """Parse Gemini response with fallbacks for malformed data."""
    try:
        candidates = response_data.get("candidates", [])
        if not candidates:
            # Sometimes the API returns empty candidates
            return {"type": "error", "message": "No candidates in response"}
        
        candidate = candidates[0]
        
        # Check for finish reason issues
        finish_reason = candidate.get("finishReason", "")
        if finish_reason == "SAFETY":
            return {"type": "blocked", "message": "Response blocked by safety filters"}
        
        content = candidate.get("content", {})
        parts = content.get("parts", [])
        
        if not parts:
            return {"type": "error", "message": "Empty response parts"}
        
        return {"type": "success", "parts": parts}
        
    except (KeyError, IndexError, TypeError) as e:
        return {"type": "error", "message": f"Malformed response: {e}"}


# =========================
# ERROR PATTERN 3: API call with retry + backoff
# =========================

def call_gemini_robust(contents: list, tool_declarations: list = None, max_retries: int = 3) -> dict:
    """API call with exponential backoff on rate limits and transient errors."""
    
    body = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": "You are a helpful assistant. Be concise."}]}
    }
    if tool_declarations:
        body["tools"] = [{"functionDeclarations": tool_declarations}]
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(
                GEMINI_URL,
                headers={"Content-Type": "application/json"},
                json=body,
                timeout=30  # 30 second timeout
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limited — exponential backoff
                wait = (2 ** attempt) + 1
                print(f"    [rate-limit] 429 received. Waiting {wait}s... (attempt {attempt+1})")
                time.sleep(wait)
                continue
            elif response.status_code >= 500:
                # Server error — retry
                wait = (2 ** attempt)
                print(f"    [server-error] {response.status_code}. Waiting {wait}s... (attempt {attempt+1})")
                time.sleep(wait)
                continue
            else:
                # Client error — don't retry
                raise Exception(f"API error {response.status_code}: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"    [timeout] Request timed out (attempt {attempt+1})")
            if attempt < max_retries:
                continue
            raise Exception("API request timed out after all retries")
        except requests.exceptions.ConnectionError:
            print(f"    [connection] Connection failed (attempt {attempt+1})")
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                continue
            raise Exception("Cannot connect to API after all retries")
    
    raise Exception(f"API call failed after {max_retries + 1} attempts")


# =========================
# ERROR PATTERN 4: Agent loop with stuck detection
# =========================

def run_robust_agent(query: str, max_iterations: int = 10) -> str:
    """Agent loop with all error handling patterns."""
    
    TOOL_DECLARATIONS = [
        {"name": "calculator", "description": "Calculate math expressions.",
         "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}},
    ]
    
    contents = [{"role": "user", "parts": [{"text": query}]}]
    
    print(f"\n{'='*60}")
    print(f"ROBUST AGENT")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    # Stuck detection: track repeated tool calls
    recent_calls = []
    
    for i in range(max_iterations):
        print(f"\n--- Step {i+1}/{max_iterations} ---")
        
        # Robust API call
        try:
            response_data = call_gemini_robust(contents, TOOL_DECLARATIONS)
        except Exception as e:
            print(f"  ✗ API call failed: {e}")
            return f"I encountered an error: {e}. Please try again."
        
        # Robust response parsing
        parsed = robust_parse_response(response_data)
        
        if parsed["type"] == "error":
            print(f"  ✗ Parse error: {parsed['message']}")
            return f"I received an unexpected response. Please try again."
        
        if parsed["type"] == "blocked":
            print(f"  ✗ {parsed['message']}")
            return "I'm unable to answer that question due to content guidelines."
        
        parts = parsed["parts"]
        contents.append({"role": "model", "parts": parts})
        
        has_func_call = False
        for part in parts:
            if "functionCall" in part:
                has_func_call = True
                fc = part["functionCall"]
                tool_name = fc["name"]
                tool_args = fc.get("args", {})
                
                # Stuck detection
                call_sig = f"{tool_name}({json.dumps(tool_args, sort_keys=True)})"
                recent_calls.append(call_sig)
                
                # Check for repeated identical calls (stuck in a loop)
                if len(recent_calls) >= 3 and len(set(recent_calls[-3:])) == 1:
                    print(f"  ⚠ STUCK DETECTED: Same tool called 3 times: {call_sig}")
                    print(f"  → Breaking loop and returning partial answer")
                    return f"I got stuck trying to use {tool_name}. The tool kept returning the same result."
                
                # Safe tool execution with retry
                print(f"  → {tool_name}({json.dumps(tool_args)[:60]})")
                result = safe_tool_call(safe_calculator, tool_args.get("expression", ""))
                print(f"  → Result: {result[:100]}")
                
                contents.append({
                    "role": "user",
                    "parts": [{"functionResponse": {"name": tool_name, "response": {"result": str(result)}}}]
                })
            
            elif "text" in part:
                print(f"  → Text: {part['text'][:100]}")
        
        if not has_func_call:
            text = " ".join(p.get("text", "") for p in parts if "text" in p)
            print(f"\n✓ Answer: {text[:200]}")
            return text
    
    print(f"\n⚠ Max iterations ({max_iterations}) reached")
    return "I couldn't complete the task within the allowed steps. Please try a simpler query."


# =========================
# STEP 5: Demo all error patterns
# =========================
if __name__ == "__main__":
    # Test 1: Normal query (should work fine)
    print("\nTEST 1: Normal query")
    run_robust_agent("What is 42 * 17?")
    
    # Test 2: Division by zero
    print("\n\nTEST 2: Division by zero")
    result = safe_calculator("10 / 0")
    print(f"  Calculator result: {result}")
    
    # Test 3: Invalid expression
    print("\n\nTEST 3: Invalid expression")
    result = safe_calculator("import os; os.system('rm -rf /')")
    print(f"  Calculator result: {result}")
    
    # Test 4: Unreliable tool with retry
    print("\n\nTEST 4: Unreliable tool with retry")
    for i in range(5):
        result = safe_tool_call(unreliable_search, "test query", max_retries=2)
        print(f"  Attempt {i+1}: {result[:80]}")
    
    print("""
    ERROR HANDLING PATTERNS:
    
    ┌──────────────────────────────────────────────────────────┐
    │ PATTERN              │ SOLUTION                          │
    ├──────────────────────┼───────────────────────────────────┤
    │ Tool throws exception│ try/except per tool + error msg   │
    │ Malformed LLM output │ Fallback parsing + default values │
    │ API rate limit (429) │ Exponential backoff + retry       │
    │ API server error     │ Retry with backoff                │
    │ API timeout          │ requests.timeout + retry          │
    │ Agent stuck in loop  │ Track recent calls + break        │
    │ Safety filter block  │ Detect + return graceful message  │
    │ Max iterations       │ Hard limit + partial answer       │
    │ Dangerous input      │ Input validation (sanitize eval)  │
    └──────────────────────┴───────────────────────────────────┘
    """)

    # KEY OBSERVATION:
    # - Error handling is BORING but ESSENTIAL for production
    # - Every tool call needs try/except
    # - Every API call needs retry with backoff
    # - Every loop needs a max iteration limit
    # - The agent should NEVER crash — always return something useful
    #
    # → File 05: Evaluation — how do you know if your agent is actually good?
