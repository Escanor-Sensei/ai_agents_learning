import os
from dotenv import load_dotenv

load_dotenv()


def get_llm():
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            streaming=True,
        )

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            streaming=True,
        )

    from langchain_ollama import ChatOllama
    return ChatOllama(model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"), streaming=True)
