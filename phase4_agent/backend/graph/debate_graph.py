from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from agents.pro_agent import pro_opening, pro_rebuttal, pro_closing
from agents.con_agent import con_opening, con_rebuttal, con_closing
from agents.moderator import load_memory, declare_winner, store_debate, decide_next_phase


class DebateGraphState(TypedDict):
    topic: str
    past_debates: list[dict]
    pro_opening: str
    con_opening: str
    pro_rebuttal: str
    con_rebuttal: str
    pro_closing: str
    con_closing: str
    winner: str
    summary: str
    next_phase: str


# ── nodes ──────────────────────────────────────────────────────────────────

def load_memory_node(state: DebateGraphState) -> dict:
    past = load_memory(state["topic"])
    return {"past_debates": past}


def pro_opening_node(state: DebateGraphState) -> dict:
    result = pro_opening(state["topic"], state["past_debates"])
    return {"pro_opening": result}


def con_opening_node(state: DebateGraphState) -> dict:
    result = con_opening(state["topic"], state["pro_opening"], state["past_debates"])
    return {"con_opening": result}


def pro_rebuttal_node(state: DebateGraphState) -> dict:
    result = pro_rebuttal(state["topic"], state["con_opening"], state["past_debates"])
    return {"pro_rebuttal": result}


def con_rebuttal_node(state: DebateGraphState) -> dict:
    result = con_rebuttal(state["topic"], state["pro_opening"], state["past_debates"])
    return {"con_rebuttal": result}


def pro_closing_node(state: DebateGraphState) -> dict:
    result = pro_closing(state["topic"], state["past_debates"])
    return {"pro_closing": result}


def con_closing_node(state: DebateGraphState) -> dict:
    result = con_closing(state["topic"], state["past_debates"])
    return {"con_closing": result}


def moderator_route_node(state: DebateGraphState) -> dict:
    pro_args = {"opening": state["pro_opening"], "rebuttal": state.get("pro_rebuttal", "")}
    con_args = {"opening": state["con_opening"], "rebuttal": state.get("con_rebuttal", "")}
    # after_rebuttal=True when rebuttal already happened — restricts options to closing/end only
    after_rebuttal = bool(state.get("pro_rebuttal", ""))
    next_phase = decide_next_phase(state["topic"], pro_args, con_args, after_rebuttal=after_rebuttal)
    return {"next_phase": next_phase}


def moderator_node(state: DebateGraphState) -> dict:
    pro_args = {
        "opening": state["pro_opening"],
        "rebuttal": state.get("pro_rebuttal", ""),
        "closing": state.get("pro_closing", ""),
    }
    con_args = {
        "opening": state["con_opening"],
        "rebuttal": state.get("con_rebuttal", ""),
        "closing": state.get("con_closing", ""),
    }
    decision = declare_winner(state["topic"], pro_args, con_args)
    summary = store_debate(state["topic"], pro_args, con_args, decision)
    return {"winner": decision.winner, "summary": summary}


def route_after_moderator(state: DebateGraphState) -> str:
    return {
        "rebuttal": "pro_rebuttal",
        "closing":  "pro_closing",
        "end":      "moderator",
    }[state["next_phase"]]


# ── graph ──────────────────────────────────────────────────────────────────

def build_graph():
    graph = StateGraph(DebateGraphState)

    graph.add_node("load_memory", load_memory_node)
    graph.add_node("pro_opening", pro_opening_node)
    graph.add_node("con_opening", con_opening_node)
    graph.add_node("moderator_route", moderator_route_node)
    graph.add_node("pro_rebuttal", pro_rebuttal_node)
    graph.add_node("con_rebuttal", con_rebuttal_node)
    graph.add_node("pro_closing", pro_closing_node)
    graph.add_node("con_closing", con_closing_node)
    graph.add_node("moderator", moderator_node)

    graph.add_edge(START, "load_memory")
    graph.add_edge("load_memory", "pro_opening")
    graph.add_edge("pro_opening", "con_opening")
    graph.add_edge("con_opening", "moderator_route")   # moderator decides after openings
    graph.add_conditional_edges("moderator_route", route_after_moderator)
    graph.add_edge("pro_rebuttal", "con_rebuttal")
    graph.add_edge("con_rebuttal", "moderator_route")  # same node reused after rebuttal
    graph.add_edge("pro_closing", "con_closing")
    graph.add_edge("con_closing", "moderator")
    graph.add_edge("moderator", END)

    return graph.compile()
