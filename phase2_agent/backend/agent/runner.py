"""
Agent Runner — agent/runner.py
Responsible for session management and invoking the agent.

.NET analogy:
  This file = AgentController / AgentService.Execute()
  AgentRunner class = a scoped service that holds session state
  run() = the method your controller calls per user request

Separation of concerns:
  core.py   → HOW the agent is built  (construction)
  runner.py → HOW the agent is used   (execution + session)
  app.py    → HOW the user interacts  (I/O only)
"""

import uuid
from langchain_core.messages import HumanMessage

from agent.core import build_agent
from memory import build_config


class AgentRunner:
    """
    Manages a single conversation session.
    Holds the agent and session config — call run() for each user turn.

    .NET analogy:
      Like a scoped IAgentService where the session ID is set on construction
      and reused across multiple calls within the same HTTP session.
    """

    def __init__(self):
        self.agent, self.tools, self.model = build_agent()

        # New session ID per AgentRunner instance
        # .NET analogy: Guid.NewGuid() assigned to a session cookie
        self.session_id = str(uuid.uuid4())
        self.config = build_config(self.session_id)

    def run(self, user_input: str) -> str:
        """
        Sends user input through the ReAct loop and returns the final answer.
        Memory is automatically loaded and saved via the checkpointer.
        """
        result = self.agent.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=self.config,
        )
        return result["messages"][-1].content
