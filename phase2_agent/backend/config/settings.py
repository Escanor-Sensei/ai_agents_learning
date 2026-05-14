"""
Settings — config/settings.py
Single source of truth for all environment config.

.NET analogy:
  This file ≈ IOptions<AppSettings> populated from appsettings.json
  All other modules import from here instead of calling os.getenv() directly.
"""

import os
from dotenv import load_dotenv

load_dotenv()

DB_CONNECTION_STRING: str = os.getenv("DB_CONNECTION_STRING", "")

# LLM provider config
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not DB_CONNECTION_STRING:
    raise EnvironmentError("DB_CONNECTION_STRING is not set in .env")
