"""
app.py — Entry point. CLI only.
All agent logic lives in agent/. This file only handles user I/O.

.NET analogy:
  This file = Program.cs — just bootstraps and runs the app.
  AgentRunner = the service doing all the real work.
"""

from agent import AgentRunner


def main():
    runner = AgentRunner()

    print("=== ReAct Agent (LangGraph + Memory) ===")
    print(f"Model   : {runner.model}")
    print(f"Tools   : {[t.name for t in runner.tools]}")
    print(f"Session : {runner.session_id[:8]}...")
    print("Memory  : short-term (in-RAM, resets on restart)")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            break

        if not user_input:
            continue

        reply = runner.run(user_input)
        print(f"\nAI: {reply}\n")
        print("-" * 50)


if __name__ == "__main__":
    main()
