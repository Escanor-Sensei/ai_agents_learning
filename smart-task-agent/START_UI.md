# Quick Start Guide - Smart Task Agent UI

## Step-by-Step Instructions

### 1️⃣ Install Node.js (if not installed)

Download from: **https://nodejs.org/**
- Choose the LTS version
- Run the installer
- Check installation: `node --version`

### 2️⃣ Install Python Dependencies

```powershell
cd "C:\Users\nihal.sinha\source\repos\Agentic AI\smart-task-agent"
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn python-multipart
```

### 3️⃣ Install UI Dependencies

```powershell
cd ui
npm install
```

This will install:
- Vue 3
- Vite
- Axios

### 4️⃣ Start the Backend Server (Terminal 1)

```powershell
# From project root, with venv activated
python api_server.py
```

You should see:
```
🚀 Starting Smart Task Agent API Server
📍 API: http://localhost:8000
📚 Docs: http://localhost:8000/docs
```

### 5️⃣ Start the Frontend (Terminal 2)

```powershell
# Open a NEW terminal
cd "C:\Users\nihal.sinha\source\repos\Agentic AI\smart-task-agent\ui"
npm run dev
```

You should see:
```
VITE v5.x.x  ready in XXX ms

➜  Local:   http://localhost:3000/
```

### 6️⃣ Open the UI

Navigate to: **http://localhost:3000**

## Using the UI

1. **Select an agent** from the left sidebar (01 - 07)
2. **Type your message** in the input box at the bottom
3. **Press Enter** or click the send button
4. **View the agent's response** in the chat area

## Example Queries to Try

**01 - Prompt:**
```
What is an AI agent in one sentence?
```

**02 - Workflow:**
```
Machine Learning
```
(It will ask for a topic - type any topic you want researched)

**03 - Agent:**
```
What is 25 * 13 + 7?
```

**03 - Agent (two tools):**
```
How many characters are in 'artificial' times 5?
```

## Troubleshooting

### ❌ "Cannot find module 'vue'"
**Fix:** Run `npm install` in the `ui` folder

### ❌ "Connection refused" error in UI
**Fix:** Make sure backend is running on port 8000

### ❌ "Module not found: fastapi"
**Fix:** Activate venv and run `pip install fastapi uvicorn`

### ❌ Agent returns error
**Fix:** Check that your Gemini API key is set in `.env`

## Keyboard Shortcuts

- **Enter**: Send message
- **Shift+Enter**: New line in message
- **Clear Chat** button: Reset conversation

## Architecture

```
Browser (localhost:3000)
     ↓ HTTP Request
Vite Dev Server
     ↓ Proxy to /api/*
FastAPI Backend (localhost:8000)
     ↓ Execute
Python Agent Scripts (day1/*.py)
     ↓ Call
Gemini API
```

Enjoy testing your agents! 🚀
