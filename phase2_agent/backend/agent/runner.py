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
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from agent.core import build_agent
from memory import build_config
from schemas import AgentResponse, ToolCall


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

    def run(self, user_input: str, history: list[dict] | None = None) -> AgentResponse:
        """
        Sends user input through the ReAct loop and returns a typed AgentResponse.
        history: prior messages from DB [{role, content}] — used to seed long-term memory
                 on a fresh session (new tab / server restart).
        """
        if history:
            seed = [
                HumanMessage(content=m["content"]) if m["role"] == "user"
                else AIMessage(content=m["content"])
                for m in history
            ]
            messages_input = seed + [HumanMessage(content=user_input)]
        else:
            messages_input = [HumanMessage(content=user_input)]

        result = self.agent.invoke(
            {"messages": messages_input},
            config=self.config,
        )

        messages = result["messages"]
        reply = messages[-1].content

        # Pair each AIMessage tool_call with its matching ToolMessage output
        tool_calls: list[ToolCall] = []
        tool_outputs: dict[str, str] = {
            m.tool_call_id: m.content
            for m in messages
            if isinstance(m, ToolMessage)
        }
        for m in messages:
            if isinstance(m, AIMessage) and m.tool_calls:
                for tc in m.tool_calls:
                    tool_calls.append(ToolCall(
                        name=tc["name"],
                        input=str(tc["args"]),
                        output=tool_outputs.get(tc["id"], ""),
                    ))

        return AgentResponse(
            reply=reply,
            session_id=self.session_id,
            model=self.model,
            tool_calls=tool_calls,
        )
