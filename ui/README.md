# Smart Task Agent - Vue.js UI

Professional chatbot interface for testing Day 1 agent scripts.

## Features

- 🎨 Modern dark theme UI
- 💬 Chat-based interface
- 🤖 Test all 7 Day 1 agents
- ⚡ Real-time execution
- 📊 Formatted output display

## Setup Instructions

### 1. Install Node.js

Download from: https://nodejs.org/ (LTS version recommended)

### 2. Install Dependencies

```bash
cd ui
npm install
```

### 3. Start the Backend API

Open a terminal in the project root:

```powershell
cd "C:\Users\nihal.sinha\source\repos\Agentic AI\smart-task-agent"
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn
python api_server.py
```

The API will start on http://localhost:8000

### 4. Start the Frontend

Open another terminal in the `ui` folder:

```bash
cd ui
npm run dev
```

The UI will open at http://localhost:3000

## Usage

1. **Select an agent** from the sidebar (01 - 07)
2. **Type your message** in the input field
3. **Press Enter** or click Send
4. **View the output** from the agent

## Architecture

```
smart-task-agent/
├── ui/                    # Vue.js frontend
│   ├── src/
│   │   ├── App.vue       # Main component
│   │   ├── main.js       # Entry point
│   │   └── style.css     # Global styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── api_server.py          # FastAPI backend
├── day1/                  # Agent scripts
│   ├── 01_prompt.py
│   ├── 02_workflow.py
│   └── ...
└── .venv/                 # Python virtual environment
```

## Tech Stack

- **Frontend**: Vue 3 + Vite
- **Backend**: FastAPI + Python
- **Communication**: Axios + REST API

## Troubleshooting

### Backend won't start
- Make sure Python virtual environment is activated
- Install missing packages: `pip install fastapi uvicorn`

### Frontend shows API errors
- Ensure backend is running on port 8000
- Check CORS settings in `api_server.py`

### Agent execution fails
- Verify Gemini API key is set in `.env`
- Check agent script exists in `day1/` folder
