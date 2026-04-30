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
    """List all available agents across all days"""
    agents = [
        # Day 1: Foundations
        {"id": "d1_01_prompt", "file": "day1/01_prompt.py", "name": "Prompt", "day": 1, "description": "Single LLM call"},
        {"id": "d1_02_workflow", "file": "day1/02_workflow.py", "name": "Workflow", "day": 1, "description": "Chained LLM calls"},
        {"id": "d1_03_agent", "file": "day1/03_agent.py", "name": "Agent", "day": 1, "description": "LLM-controlled loop"},
        {"id": "d1_04_raw_prompt", "file": "day1/04_raw_prompt.py", "name": "Raw Prompt", "day": 1, "description": "Raw HTTP call"},
        {"id": "d1_05_raw_agent_loop", "file": "day1/05_raw_agent_loop.py", "name": "Raw Agent Loop", "day": 1, "description": "Agent from scratch"},
        {"id": "d1_06_first_agent", "file": "day1/06_first_agent.py", "name": "First Agent", "day": 1, "description": "Framework agent"},
        {"id": "d1_07_raw_react", "file": "day1/07_raw_react.py", "name": "Raw ReAct", "day": 1, "description": "Raw ReAct pattern"},
        # Day 2: Planning & Execution
        {"id": "d2_01_planning_intro", "file": "day2/01_planning_intro.py", "name": "Planning Intro", "day": 2, "description": "Plan-then-Execute vs ReAct"},
        {"id": "d2_02_raw_planning", "file": "day2/02_raw_planning.py", "name": "Raw Planning", "day": 2, "description": "Raw two-phase planning"},
        {"id": "d2_03_react_deep_dive", "file": "day2/03_react_deep_dive.py", "name": "ReAct Deep Dive", "day": 2, "description": "Tracing ReAct loop internals"},
        {"id": "d2_04_raw_react_patterns", "file": "day2/04_raw_react_patterns.py", "name": "Raw ReAct Patterns", "day": 2, "description": "Enhanced loop with observability"},
        {"id": "d2_05_plan_vs_react", "file": "day2/05_plan_vs_react.py", "name": "Plan vs ReAct", "day": 2, "description": "Side-by-side comparison"},
        {"id": "d2_06_task_build_planner", "file": "day2/06_task_build_planner.py", "name": "Task: Planner", "day": 2, "description": "Build a planning agent"},
        {"id": "d2_07_predict_debug", "file": "day2/07_predict_debug.py", "name": "Predict & Debug", "day": 2, "description": "Planning debugging exercises"},
        {"id": "d2_08_reference_solution", "file": "day2/08_reference_solution.py", "name": "Reference Solution", "day": 2, "description": "Planner solution"},
        # Day 3: Tool Use & Memory
        {"id": "d3_01_real_tools", "file": "day3/01_real_tools.py", "name": "Real Tools", "day": 3, "description": "5 real tools + agent"},
        {"id": "d3_02_tool_schemas", "file": "day3/02_tool_schemas.py", "name": "Tool Schemas", "day": 3, "description": "How LLMs choose tools"},
        {"id": "d3_03_raw_tool_registry", "file": "day3/03_raw_tool_registry.py", "name": "Raw Tool Registry", "day": 3, "description": "Manual tool dispatch"},
        {"id": "d3_04_dynamic_selection", "file": "day3/04_dynamic_selection.py", "name": "Dynamic Selection", "day": 3, "description": "7 tools auto-routing"},
        {"id": "d3_05_short_term_memory", "file": "day3/05_short_term_memory.py", "name": "Short-Term Memory", "day": 3, "description": "Conversation context"},
        {"id": "d3_06_raw_short_term", "file": "day3/06_raw_short_term.py", "name": "Raw Short-Term", "day": 3, "description": "Raw conversation memory"},
        {"id": "d3_07_long_term_memory", "file": "day3/07_long_term_memory.py", "name": "Long-Term Memory", "day": 3, "description": "Persistent JSON memory"},
        {"id": "d3_08_raw_long_term", "file": "day3/08_raw_long_term.py", "name": "Raw Long-Term", "day": 3, "description": "Raw persistent memory"},
        {"id": "d3_09_task_tool_and_memory", "file": "day3/09_task_tool_and_memory.py", "name": "Task: Tools + Memory", "day": 3, "description": "Build tools + memory agent"},
        {"id": "d3_10_predict_debug", "file": "day3/10_predict_debug.py", "name": "Predict & Debug", "day": 3, "description": "Memory debugging exercises"},
        {"id": "d3_11_reference_solution", "file": "day3/11_reference_solution.py", "name": "Reference Solution", "day": 3, "description": "Tool + memory agent solution"},
        # Day 4: Build — Simple Agent
        {"id": "d4_01_simple_agent_framework", "file": "day4/01_simple_agent_framework.py", "name": "Simple Agent", "day": 4, "description": "Framework agent step-by-step"},
        {"id": "d4_02_raw_simple_agent", "file": "day4/02_raw_simple_agent.py", "name": "Raw Simple Agent", "day": 4, "description": "Raw agent from scratch"},
        {"id": "d4_03_add_second_tool", "file": "day4/03_add_second_tool.py", "name": "Two Tools", "day": 4, "description": "Agent with tool selection"},
        {"id": "d4_04_raw_two_tools", "file": "day4/04_raw_two_tools.py", "name": "Raw Two Tools", "day": 4, "description": "Raw agent with two tools"},
        {"id": "d4_05_task_build_agent", "file": "day4/05_task_build_agent.py", "name": "Task: Build Agent", "day": 4, "description": "Build your own agent"},
        {"id": "d4_06_predict_debug", "file": "day4/06_predict_debug.py", "name": "Predict & Debug", "day": 4, "description": "Agent debugging exercises"},
        {"id": "d4_07_reference_solution", "file": "day4/07_reference_solution.py", "name": "Reference Solution", "day": 4, "description": "Simple agent solution"},
    ]
    return {"agents": agents}

@app.post("/api/execute")
async def execute_agent(request: AgentRequest) -> AgentResponse:
    """Execute a Python agent script with user input"""
    
    # Security: Validate agent file name (format: dayN/script.py)
    allowed_files = [
        # Day 1
        "day1/01_prompt.py", "day1/02_workflow.py", "day1/03_agent.py",
        "day1/04_raw_prompt.py", "day1/05_raw_agent_loop.py",
        "day1/06_first_agent.py", "day1/07_raw_react.py",
        # Day 2
        "day2/01_planning_intro.py", "day2/02_raw_planning.py",
        "day2/03_react_deep_dive.py", "day2/04_raw_react_patterns.py",
        "day2/05_plan_vs_react.py", "day2/06_task_build_planner.py",
        "day2/07_predict_debug.py", "day2/08_reference_solution.py",
        # Day 3
        "day3/01_real_tools.py", "day3/02_tool_schemas.py", "day3/03_raw_tool_registry.py",
        "day3/04_dynamic_selection.py", "day3/05_short_term_memory.py", "day3/06_raw_short_term.py",
        "day3/07_long_term_memory.py", "day3/08_raw_long_term.py",
        "day3/09_task_tool_and_memory.py", "day3/10_predict_debug.py", "day3/11_reference_solution.py",
        # Day 4
        "day4/01_simple_agent_framework.py", "day4/02_raw_simple_agent.py",
        "day4/03_add_second_tool.py", "day4/04_raw_two_tools.py",
        "day4/05_task_build_agent.py", "day4/06_predict_debug.py", "day4/07_reference_solution.py",
    ]
    
    if request.agent not in allowed_files:
        raise HTTPException(status_code=400, detail=f"Invalid agent file: {request.agent}")
    
    # Build path to the agent script (agent field is now "dayN/script.py")
    script_path = os.path.join(os.path.dirname(__file__), request.agent)
    
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
