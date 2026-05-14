import uuid
from langchain_core.documents import Document
from memory.vector_store import get_vector_store


def save_debate(topic: str, pro_args: str, con_args: str, winner: str, summary: str):
    doc = Document(
        page_content=f"Topic: {topic}\nSummary: {summary}",
        metadata={
            "id": str(uuid.uuid4()),
            "topic": topic,
            "pro_args": pro_args,
            "con_args": con_args,
            "winner": winner,
        },
    )
    store = get_vector_store()
    store.add_documents([doc])


def get_relevant_debates(topic: str, k: int = 2) -> list[dict]:
    store = get_vector_store()
    results = store.similarity_search(topic, k=k)
    return [
        {
            "topic": doc.metadata["topic"],
            "pro_args": doc.metadata["pro_args"],
            "con_args": doc.metadata["con_args"],
            "winner": doc.metadata["winner"],
        }
        for doc in results
    ]
