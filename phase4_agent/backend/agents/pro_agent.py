from langchain_core.messages import SystemMessage, HumanMessage
from config import get_llm

_llm = get_llm()

_SYSTEM = """You are a skilled debater arguing IN FAVOR of the given topic.
You have access to context from past debates — use it to evolve your arguments, not repeat them.
Be persuasive, logical, and direct. Never mention that you are referencing past debates."""


def _build_context(past_debates: list[dict]) -> str:
    if not past_debates:
        return ""
    lines = ["Context from related past debates:"]
    for d in past_debates:
        lines.append(f"- Topic: {d['topic']} | Pro argued: {d['pro_args'][:200]}")
    return "\n".join(lines)


def pro_opening(topic: str, past_debates: list[dict]) -> str:
    context = _build_context(past_debates)
    response = _llm.invoke([
        SystemMessage(content=_SYSTEM),
        HumanMessage(content=f"{context}\n\nPresent your opening argument (~200 words) in favor of: {topic}"),
    ])
    return response.content


def pro_rebuttal(topic: str, con_opening: str, past_debates: list[dict]) -> str:
    context = _build_context(past_debates)
    response = _llm.invoke([
        SystemMessage(content=_SYSTEM),
        HumanMessage(content=(
            f"{context}\n\n"
            f"Topic: {topic}\n\n"
            f"Con Agent argued:\n{con_opening}\n\n"
            "Write a rebuttal (~100 words) countering the above arguments."
        )),
    ])
    return response.content


def pro_closing(topic: str, past_debates: list[dict]) -> str:
    context = _build_context(past_debates)
    response = _llm.invoke([
        SystemMessage(content=_SYSTEM),
        HumanMessage(content=f"{context}\n\nGive your closing remarks (~50-100 words) in favor of: {topic}"),
    ])
    return response.content
