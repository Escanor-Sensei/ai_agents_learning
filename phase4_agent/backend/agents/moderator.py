from langchain_core.messages import SystemMessage, HumanMessage
from config import get_llm
from schemas import ModeratorDecision, ModeratorRouteDecision
from memory.debate_store import get_relevant_debates, save_debate

_llm = get_llm()

_structured_llm = _llm.with_structured_output(ModeratorDecision)
_routing_llm    = _llm.with_structured_output(ModeratorRouteDecision)

_SYSTEM = """You are an impartial debate moderator.
Evaluate both sides fairly based on argument quality, logic, and persuasiveness.
Declare a winner with clear justification."""

_ROUTING_SYSTEM = """You are a debate moderator controlling the flow of a debate.
Based on the arguments so far, decide what should happen next:
- 'rebuttal': arguments are close and another rebuttal round is needed
- 'closing': enough has been said, move to closing statements
- 'end': one side is clearly dominant, skip closing and go straight to verdict"""


def decide_next_phase(topic: str, pro_args: dict, con_args: dict, after_rebuttal: bool = False) -> str:
    """
    Moderator dynamically decides the next phase of the debate.
    After openings:  returns 'rebuttal', 'closing', or 'end'.
    After rebuttal:  returns 'closing' or 'end' only.
    """
    if after_rebuttal:
        system = """You are a debate moderator controlling the flow of a debate.
Based on all arguments so far, decide what should happen next:
- 'closing': both sides should give closing statements
- 'end': one side is clearly dominant, skip closing and go straight to verdict"""
    else:
        system = _ROUTING_SYSTEM

    decision = _routing_llm.invoke([
        SystemMessage(content=system),
        HumanMessage(content=(
            f"Topic: {topic}\n\n"
            f"PRO so far:\n{pro_args.get('opening', '')}\n{pro_args.get('rebuttal', '')}\n\n"
            f"CON so far:\n{con_args.get('opening', '')}\n{con_args.get('rebuttal', '')}\n\n"
            "What should happen next in this debate?"
        )),
    ])
    # Guard: after rebuttal, never return 'rebuttal' again
    if after_rebuttal and decision.next_phase == "rebuttal":
        return "closing"
    return decision.next_phase


def load_memory(topic: str) -> list[dict]:
    past = get_relevant_debates(topic)
    return past


def declare_winner(topic: str, pro_args: dict, con_args: dict) -> ModeratorDecision:
    return _structured_llm.invoke([
        SystemMessage(content=_SYSTEM),
        HumanMessage(content=(
            f"Topic: {topic}\n\n"
            f"PRO AGENT:\n"
            f"Opening: {pro_args['opening']}\n"
            f"Rebuttal: {pro_args.get('rebuttal', '')}\n"
            f"Closing: {pro_args.get('closing', '')}\n\n"
            f"CON AGENT:\n"
            f"Opening: {con_args['opening']}\n"
            f"Rebuttal: {con_args.get('rebuttal', '')}\n"
            f"Closing: {con_args.get('closing', '')}\n\n"
            "Summarize both sides and declare the winner with justification."
        )),
    ])


def store_debate(topic: str, pro_args: dict, con_args: dict, decision: ModeratorDecision) -> str:
    summary = (
        f"Pro: {decision.pro_summary}\n"
        f"Con: {decision.con_summary}\n"
        f"Winner: {decision.winner} — {decision.justification}"
    )
    save_debate(
        topic=topic,
        pro_args=pro_args["opening"],
        con_args=con_args["opening"],
        winner=decision.winner,
        summary=summary,
    )
    return summary
