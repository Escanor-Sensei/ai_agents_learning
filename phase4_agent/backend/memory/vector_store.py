import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

_embedding_model = None
_vector_store = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        )
    return _embedding_model


def get_vector_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = Chroma(
            collection_name="debates",
            embedding_function=get_embedding_model(),
            persist_directory=os.getenv("CHROMA_PERSIST_DIR", "./memory/chroma_db"),
        )
    return _vector_store
