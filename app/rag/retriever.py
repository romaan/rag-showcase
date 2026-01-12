from __future__ import annotations
import json
from typing import Optional
from app.db.pg import conn
from app.config import settings

def vector_search(query_embedding: list[float], top_k: int, filter_source: Optional[str] = None):
    """
    cosine distance => smaller is better. We return score as (1 - distance) for readability.
    """
    top_k = top_k or settings.TOP_K
    where = ""
    params = [query_embedding, top_k]
    if filter_source:
        where = "WHERE d.source = %s"
        params = [query_embedding, filter_source, top_k]

    sql = f"""
    SELECT
      e.chunk_id,
      1 - (e.embedding <=> %s::vector) AS score,
      c.content,
      c.document_id,
      d.title,
      d.source
    FROM embeddings e
    JOIN chunks c ON c.id = e.chunk_id
    JOIN documents d ON d.id = c.document_id
    {where}
    ORDER BY e.embedding <=> %s::vector
    LIMIT %s
    """
    # Note: order-by uses the same vector; we pass it twice
    if filter_source:
        params = [query_embedding, filter_source, query_embedding, top_k]
    else:
        params = [query_embedding, query_embedding, top_k]

    with conn() as c:
        with c.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
