from langchain_core.messages import SystemMessage, HumanMessage
from config import get_llm

_llm = get_llm()

_SYSTEM = """You are a skilled debater arguing AGAINST the given topic.
You have access to context from past debates — use it to evolve your arguments, not repeat them.
Be persuasive, logical, and direct. Never mention that you are referencing past debates."""


def _build_context(past_debates: list[dict]) -> str:
    if not past_debates:
        return ""
    lines = ["Context from related past debates:"]
    for d in past_debates:
        lines.append(f"- Topic: {d['topic']} | Con argued: {d['con_args'][:200]}")
    return "\n".join(lines)


def con_opening(topic: str, pro_opening: str, past_debates: list[dict]) -> str:
    context = _build_context(past_debates)
    response = _llm.invoke([
        SystemMessage(content=_SYSTEM),
        HumanMessage(content=(
            f"{context}\n\n"
            f"Pro Agent argued:\n{pro_opening}\n\n"
            f"Present your opening argument (~200 words) against: {topic}"
        )),
    ])
    return response.content


def con_rebuttal(topic: str, pro_opening: str, past_debates: list[dict]) -> str:
    context = _build_context(past_debates)
    response = _llm.invoke([
        SystemMessage(content=_SYSTEM),
        HumanMessage(content=(
            f"{context}\n\n"
            f"Topic: {topic}\n\n"
            f"Pro Agent argued:\n{pro_opening}\n\n"
            "Write a rebuttal (~100 words) countering the above arguments."
        )),
    ])
    return response.content


def con_closing(topic: str, past_debates: list[dict]) -> str:
    context = _build_context(past_debates)
    response = _llm.invoke([
        SystemMessage(content=_SYSTEM),
        HumanMessage(content=f"{context}\n\nGive your closing remarks (~50-100 words) against: {topic}"),
    ])
    return response.content
