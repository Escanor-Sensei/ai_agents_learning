from langchain_core.messages import SystemMessage, HumanMessage
from config import get_llm
from schemas import ModeratorDecision
from memory.debate_store import get_relevant_debates, save_debate

_llm = get_llm()

_structured_llm = _llm.with_structured_output(ModeratorDecision)

_SYSTEM = """You are an impartial debate moderator.
Evaluate both sides fairly based on argument quality, logic, and persuasiveness.
Declare a winner with clear justification."""


def load_memory(topic: str) -> list[dict]:
    """
    Moderator decides whether past debates are relevant enough to use.
    Returns past debates if found, empty list otherwise.
    """
    past = get_relevant_debates(topic)
    return past


def declare_winner(topic: str, pro_args: dict, con_args: dict) -> ModeratorDecision:
    """
    pro_args / con_args: dicts with keys opening, rebuttal, closing
    Returns ModeratorDecision with pro_summary, con_summary, winner, justification
    """
    return _structured_llm.invoke([
        SystemMessage(content=_SYSTEM),
        HumanMessage(content=(
            f"Topic: {topic}\n\n"
            f"PRO AGENT:\n"
            f"Opening: {pro_args['opening']}\n"
            f"Rebuttal: {pro_args['rebuttal']}\n"
            f"Closing: {pro_args['closing']}\n\n"
            f"CON AGENT:\n"
            f"Opening: {con_args['opening']}\n"
            f"Rebuttal: {con_args['rebuttal']}\n"
            f"Closing: {con_args['closing']}\n\n"
            "Summarize both sides and declare the winner with justification."
        )),
    ])


def store_debate(topic: str, pro_args: dict, con_args: dict, decision: ModeratorDecision) -> str:
    """
    Moderator saves the debate to memory after declaring winner.
    Returns the formatted summary.
    """
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
