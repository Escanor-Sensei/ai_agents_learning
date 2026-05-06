"""
Tool: Web Search
Responsibility: Search the web using DuckDuckGo and return summarized results.

.NET analogy: An IHttpClientFactory-backed service that calls an external API.
No API key needed — DuckDuckGo is free and local-friendly.
"""

from langchain_core.tools import tool

try:
    from ddgs import DDGS
except ModuleNotFoundError:
    from duckduckgo_search import DDGS


@tool
def web_search(query: str) -> str:
    """
    Searches the web for current information using DuckDuckGo.
    Use this tool when the user asks about recent events, news, facts you may
    not know, or anything that requires up-to-date information from the internet.
    Input should be a clear, concise search query string.
    Returns a summary of the top search results.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))

        if not results:
            return "No results found for the given query."

        # Format results like a structured response DTO
        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(f"[{i}] {r['title']}\n{r['body']}\nSource: {r['href']}")

        return "\n\n".join(formatted)

    except Exception as e:
        return f"Web search error: {e}"
