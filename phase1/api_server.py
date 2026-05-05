"""
FastAPI Backend Server for Smart Task Agent UI
Simple API that runs one configurable Python agent script
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import subprocess
import asyncio
import os
import sys
import json

# ============================================================
# CONFIGURATION - Change this to test different agents
# ============================================================
TARGET_AGENT_FILE = "day3/03_short_term_memory.py"
# ============================================================

app = FastAPI(title="Smart Task Agent API")

# Enable CORS for Vue.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    input: str

class AgentResponse(BaseModel):
    output: str
    success: bool

@app.get("/")
def read_root():
    return {
        "message": "Smart Task Agent API",
        "status": "running",
        "target_agent": TARGET_AGENT_FILE,
        "endpoints": {
            "/api/execute": "POST - Execute the configured agent"
        }
    }

@app.post("/api/execute")
async def execute_agent(request: AgentRequest) -> AgentResponse:
    """Execute the configured Python agent script with user input"""
    
    # Build path to the agent script
    script_path = os.path.join(os.path.dirname(__file__), TARGET_AGENT_FILE)
    
    if not os.path.exists(script_path):
        raise HTTPException(status_code=404, detail=f"Agent script not found: {TARGET_AGENT_FILE}")
    
    try:
        # Activate virtual environment and run the script
        venv_python = os.path.join(os.path.dirname(__file__), ".venv", "Scripts", "python.exe")
        
        # Use venv python if it exists, otherwise use system python
        python_exe = venv_python if os.path.exists(venv_python) else sys.executable
        
        # Execute the agent script
        # Pass user input via stdin for scripts that need it
        result = subprocess.run(
            [python_exe, script_path],
            input=request.input,
            capture_output=True,
            text=True,
            timeout=120,  # 120 second timeout for reflection loops
            cwd=os.path.dirname(script_path)  # Run from day directory
        )
        
        # Combine stdout and stderr for complete output
        output = result.stdout
        if result.stderr:
            output += f"\n\n--- Errors/Warnings ---\n{result.stderr}"
        
        # Debug logging
        print(f"[DEBUG] Script executed. Return code: {result.returncode}")
        print(f"[DEBUG] Output length: {len(output)} characters")
        print(f"[DEBUG] First 200 chars: {output[:200]}...")
        
        if result.returncode != 0:
            # Script failed but we got output
            return AgentResponse(
                output=output or "Script failed with no output",
                success=False
            )
        
        return AgentResponse(
            output=output or "Script completed with no output",
            success=True
        )
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Script execution timed out (60s limit)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

@app.post("/api/stream")
async def stream_agent(request: AgentRequest):
    """Execute the agent script and stream stdout line-by-line as SSE."""
    script_path = os.path.join(os.path.dirname(__file__), TARGET_AGENT_FILE)

    if not os.path.exists(script_path):
        raise HTTPException(status_code=404, detail=f"Agent script not found: {TARGET_AGENT_FILE}")

    venv_python = os.path.join(os.path.dirname(__file__), ".venv", "Scripts", "python.exe")
    python_exe = venv_python if os.path.exists(venv_python) else sys.executable

    async def event_generator():
        try:
            proc = await asyncio.create_subprocess_exec(
                python_exe, script_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.path.dirname(script_path),
            )

            # Send user input then close stdin so the script can start
            if request.input:
                proc.stdin.write((request.input + "\n").encode())
                await proc.stdin.drain()
            proc.stdin.close()

            # Stream stdout lines as they arrive
            async for line in proc.stdout:
                text = line.decode("utf-8", errors="replace")
                payload = json.dumps({"chunk": text, "done": False})
                yield f"data: {payload}\n\n"

            await proc.wait()

            # Send any stderr as a final chunk
            stderr_bytes = await proc.stderr.read()
            if stderr_bytes:
                stderr_text = stderr_bytes.decode("utf-8", errors="replace")
                payload = json.dumps({"chunk": f"\n\n--- Errors/Warnings ---\n{stderr_text}", "done": False})
                yield f"data: {payload}\n\n"

            # Signal completion
            payload = json.dumps({"chunk": "", "done": True, "success": proc.returncode == 0})
            yield f"data: {payload}\n\n"

        except asyncio.CancelledError:
            if proc and proc.returncode is None:
                proc.kill()
        except Exception as e:
            payload = json.dumps({"chunk": f"[ERROR] {str(e)}", "done": True, "success": False})
            yield f"data: {payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 Starting Smart Task Agent API Server")
    print("=" * 60)
    print(f"🤖 Target Agent: {TARGET_AGENT_FILE}")
    print(f"📍 API: http://localhost:8000")
    print(f"📚 Docs: http://localhost:8000/docs")
    print(f"🎨 UI: http://localhost:3000 or :3001")
    print("=" * 60)
    print("💡 To test a different agent, change TARGET_AGENT_FILE")
    print("   at the top of this file and restart the server.")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
