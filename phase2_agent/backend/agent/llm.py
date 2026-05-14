"""
LLM Factory — agent/llm.py

Single place to swap the underlying model. Set LLM_PROVIDER in .env:
  LLM_PROVIDER=gemini   → uses ChatGoogleGenerativeAI (GEMINI_MODEL + GOOGLE_API_KEY)
  LLM_PROVIDER=ollama   → uses ChatOllama            (OLLAMA_MODEL)
  LLM_PROVIDER=openai   → uses ChatOpenAI            (OPENAI_MODEL + OPENAI_API_KEY)

No other file needs to change when switching providers — only .env.
"""

import os


def get_llm():
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    # default: ollama
    from langchain_ollama import ChatOllama
    return ChatOllama(model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"))


def get_model_name() -> str:
    """Returns the active model name for logging/response metadata."""
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider == "gemini":
        return os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")
    if provider == "openai":
        return os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
