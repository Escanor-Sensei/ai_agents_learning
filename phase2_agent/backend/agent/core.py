"""
Agent Core — agent/core.py
Responsible for building the ReAct agent graph.

.NET analogy:
  This file = builder.Services.AddScoped<IAgentService, AgentService>()
  build_agent() = the factory method that wires LLM + tools + memory together
  Nothing here knows about CLI, sessions, or user input — pure construction.
"""

import os
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

from tools import all_tools
from memory import create_memory

MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

_SYSTEM_PROMPT = "You are a helpful assistant. Use tools when needed. Be concise."


def build_agent():
    """
    Constructs and returns the ReAct agent with tools and memory wired in.

    .NET analogy:
      Like a factory method returning a fully configured IAgentService.
      Caller doesn't need to know how LLM, tools, or memory are assembled.
    """
    llm = ChatOllama(model=MODEL)
    memory = create_memory()

    agent = create_react_agent(
        model=llm,
        tools=all_tools,
        checkpointer=memory,
        prompt=_SYSTEM_PROMPT,
    )

    return agent, all_tools, MODEL
