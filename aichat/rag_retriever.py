import json
import math
from pathlib import Path
from typing import List, Dict, Any

from django.conf import settings
from openai import OpenAI


client = OpenAI(api_key=getattr(settings, "OPENAI_API_KEY", None))

INDEX_PATH = Path(settings.BASE_DIR) / "rag_index.jsonl"


def _load_index() -> List[Dict[str, Any]]:
    """
    Load prebuilt RAG index from rag_index.jsonl.
    Each line: {"doc": {...}, "embedding": [...]}
    """
    if not INDEX_PATH.exists():
        return []
    docs: List[Dict[str, Any]] = []
    with INDEX_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                item = json.loads(line)
                docs.append(item)
            except json.JSONDecodeError:
                continue
    return docs


INDEX = _load_index()


def _dot(a: List[float], b: List[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _norm(a: List[float]) -> float:
    return math.sqrt(sum(x * x for x in a))


def _cosine(a: List[float], b: List[float]) -> float:
    return _dot(a, b) / (_norm(a) * _norm(b) + 1e-9)


def embed_query(text: str) -> List[float]:
    """
    Create an embedding for a query string.
    """
    if not client.api_key:
        # No API key configured; disable RAG silently
        return []

    resp = client.embeddings.create(
        model="text-embedding-3-large",
        input=[text],
    )
    return resp.data[0].embedding


def retrieve_relevant_chunks(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve top_k most relevant documents from the local RAG index.
    Returns a list of doc dicts (without embeddings).
    """
    if not INDEX:
        return []

    q_emb = embed_query(query)
    if not q_emb:
        return []

    scored: List[tuple[float, Dict[str, Any]]] = []
    for item in INDEX:
        emb = item.get("embedding")
        doc = item.get("doc")
        if not emb or not doc:
            continue
        sim = _cosine(q_emb, emb)
        scored.append((sim, doc))

    scored.sort(reverse=True, key=lambda x: x[0])
    top = [doc for sim, doc in scored[:top_k]]
    return top


