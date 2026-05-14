from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from agents.pro_agent import pro_opening, pro_rebuttal, pro_closing
from agents.con_agent import con_opening, con_rebuttal, con_closing
from agents.moderator import load_memory, declare_winner, store_debate


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


# ── nodes ──────────────────────────────────────────────────────────────────

def load_memory_node(state: DebateGraphState) -> dict:
    # Moderator controls when and whether memory is loaded
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


def moderator_node(state: DebateGraphState) -> dict:
    pro_args = {
        "opening": state["pro_opening"],
        "rebuttal": state["pro_rebuttal"],
        "closing": state["pro_closing"],
    }
    con_args = {
        "opening": state["con_opening"],
        "rebuttal": state["con_rebuttal"],
        "closing": state["con_closing"],
    }
    decision = declare_winner(state["topic"], pro_args, con_args)
    # Moderator controls saving to memory after debate ends
    summary = store_debate(state["topic"], pro_args, con_args, decision)
    return {"winner": decision.winner, "summary": summary}


# ── graph ──────────────────────────────────────────────────────────────────

def build_graph():
    graph = StateGraph(DebateGraphState)

    graph.add_node("load_memory", load_memory_node)
    graph.add_node("pro_opening", pro_opening_node)
    graph.add_node("con_opening", con_opening_node)
    graph.add_node("pro_rebuttal", pro_rebuttal_node)
    graph.add_node("con_rebuttal", con_rebuttal_node)
    graph.add_node("pro_closing", pro_closing_node)
    graph.add_node("con_closing", con_closing_node)
    graph.add_node("moderator", moderator_node)

    graph.add_edge(START, "load_memory")
    graph.add_edge("load_memory", "pro_opening")
    graph.add_edge("pro_opening", "con_opening")
    graph.add_edge("con_opening", "pro_rebuttal")
    graph.add_edge("pro_rebuttal", "con_rebuttal")
    graph.add_edge("con_rebuttal", "pro_closing")
    graph.add_edge("pro_closing", "con_closing")
    graph.add_edge("con_closing", "moderator")
    graph.add_edge("moderator", END)

    return graph.compile()
