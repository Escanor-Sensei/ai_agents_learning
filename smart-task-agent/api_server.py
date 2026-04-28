"""
FastAPI Backend Server for Smart Task Agent UI
Executes Python agent scripts and returns results
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import os
import sys

app = FastAPI(title="Smart Task Agent API")

# Enable CORS for Vue.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    agent: str
    input: str

class AgentResponse(BaseModel):
    output: str
    success: bool

@app.get("/")
def read_root():
    return {
        "message": "Smart Task Agent API",
        "status": "running",
        "endpoints": {
            "/api/execute": "POST - Execute an agent script",
            "/api/agents": "GET - List available agents"
        }
    }

@app.get("/api/agents")
def list_agents():
    """List all available Day 1 agents"""
    agents = [
        {"id": "01_prompt", "file": "01_prompt.py", "name": "Prompt", "description": "Single LLM call"},
        {"id": "02_workflow", "file": "02_workflow.py", "name": "Workflow", "description": "Chained LLM calls"},
        {"id": "03_agent", "file": "03_agent.py", "name": "Agent", "description": "LLM-controlled loop"},
        {"id": "04_raw_prompt", "file": "04_raw_prompt.py", "name": "Raw Prompt", "description": "Raw HTTP call"},
        {"id": "05_raw_agent_loop", "file": "05_raw_agent_loop.py", "name": "Raw Agent Loop", "description": "Agent from scratch"},
        {"id": "06_first_agent", "file": "06_first_agent.py", "name": "First Agent", "description": "Framework agent"},
        {"id": "07_raw_react", "file": "07_raw_react.py", "name": "Raw ReAct", "description": "Raw ReAct pattern"}
    ]
    return {"agents": agents}

@app.post("/api/execute")
async def execute_agent(request: AgentRequest) -> AgentResponse:
    """Execute a Python agent script with user input"""
    
    # Security: Validate agent file name
    allowed_files = [
        "01_prompt.py", "02_workflow.py", "03_agent.py",
        "04_raw_prompt.py", "05_raw_agent_loop.py",
        "06_first_agent.py", "07_raw_react.py"
    ]
    
    if request.agent not in allowed_files:
        raise HTTPException(status_code=400, detail=f"Invalid agent file: {request.agent}")
    
    # Build path to the agent script
    script_path = os.path.join(os.path.dirname(__file__), "day1", request.agent)
    
    if not os.path.exists(script_path):
        raise HTTPException(status_code=404, detail=f"Agent script not found: {request.agent}")
    
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
            timeout=60,  # 60 second timeout
            cwd=os.path.dirname(script_path)  # Run from day1 directory
        )
        
        # Combine stdout and stderr for complete output
        output = result.stdout
        if result.stderr:
            output += f"\n\n--- Errors/Warnings ---\n{result.stderr}"
        
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

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 Starting Smart Task Agent API Server")
    print("=" * 60)
    print(f"📍 API: http://localhost:8000")
    print(f"📚 Docs: http://localhost:8000/docs")
    print(f"🎨 UI: Start the Vue.js frontend on port 3000")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
