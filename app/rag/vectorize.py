from __future__ import annotations
import json
from app.config import settings
from app.db.pg import conn
from app.logging import log_event

def get_embedder():
    if settings.EMBEDDINGS_PROVIDER == "ollama":
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(
            model=settings.OLLAMA_EMBED_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )
    if settings.EMBEDDINGS_PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
    # local embedder
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed_texts(texts: list[str]) -> list[list[float]]:
    emb = get_embedder()
    if settings.EMBEDDINGS_PROVIDER == "ollama":
        return emb.embed_documents(texts)
    if settings.EMBEDDINGS_PROVIDER == "openai":
        return emb.embed_documents(texts)
    vectors = emb.encode(texts, normalize_embeddings=True)
    return [v.tolist() for v in vectors]

def upsert_embeddings(chunk_ids: list[str], vectors: list[list[float]]):
    with conn() as c:
        with c.cursor() as cur:
            for cid, vec in zip(chunk_ids, vectors):
                cur.execute(
                    """
                    INSERT INTO embeddings (chunk_id, embedding)
                    VALUES (%s, %s::vector)
                    ON CONFLICT (chunk_id) DO UPDATE SET embedding=EXCLUDED.embedding
                    """,
                    (cid, vec),
                )
        c.commit()
    log_event("vectorize.upserted", chunks=len(chunk_ids))
