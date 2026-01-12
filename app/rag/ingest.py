from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Iterable, Optional
import httpx
from bs4 import BeautifulSoup

from app.db.pg import conn
from app.rag.chunking import split_text
from app.logging import log_event

def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def upsert_document(doc_id: str, source: str, title: Optional[str], metadata: dict):
    with conn() as c:
        with c.cursor() as cur:
            cur.execute(
                """
                INSERT INTO documents (id, source, title, metadata)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET source=EXCLUDED.source, title=EXCLUDED.title, metadata=EXCLUDED.metadata
                """,
                (doc_id, source, title, json.dumps(metadata)),
            )
        c.commit()

def insert_chunks(document_id: str, chunks: list[str], base_metadata: dict) -> list[str]:
    chunk_ids: list[str] = []
    with conn() as c:
        with c.cursor() as cur:
            for i, content in enumerate(chunks):
                chunk_id = _sha(f"{document_id}:{i}:{content[:64]}")
                chunk_ids.append(chunk_id)
                md = dict(base_metadata)
                md.update({"chunk_index": i})
                cur.execute(
                    """
                    INSERT INTO chunks (id, document_id, chunk_index, content, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE
                    SET content=EXCLUDED.content, metadata=EXCLUDED.metadata
                    """,
                    (chunk_id, document_id, i, content, json.dumps(md)),
                )
        c.commit()
    return chunk_ids

def load_text_file(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return path.name, text

def load_pdf_file(path: Path) -> tuple[str, str]:
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    pages = []
    for p in reader.pages:
        pages.append(p.extract_text() or "")
    return path.name, "\n".join(pages)

def load_url(url: str) -> tuple[str, str]:
    r = httpx.get(url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.title.text.strip() if soup.title else url
    # Basic main-text extraction
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    text = " ".join(soup.get_text(" ").split())
    return title, text

def ingest_local_dir(path: str) -> tuple[int, int, list[tuple[str,str,str,dict]]]:
    p = Path(path)
    items = []
    for f in p.rglob("*"):
        if not f.is_file():
            continue
        if f.suffix.lower() in [".txt", ".md"]:
            title, text = load_text_file(f)
        elif f.suffix.lower() in [".pdf"]:
            title, text = load_pdf_file(f)
        else:
            continue
        doc_id = _sha(str(f.resolve()))
        items.append((doc_id, "local", title, {"path": str(f)} | {"text": text}))
    # return list with text embedded in metadata (not stored long-term) for pipeline step
    return len(items), 0, items

def ingest_urls(urls: Iterable[str]) -> tuple[int, int, list[tuple[str,str,str,dict]]]:
    items = []
    for u in urls:
        u = u.strip()
        if not u:
            continue
        title, text = load_url(u)
        doc_id = _sha(u)
        items.append((doc_id, "url", title, {"url": u, "text": text}))
    return len(items), 0, items

def persist_docs_and_chunks(items: list[tuple[str,str,str,dict]]) -> tuple[int,int,list[tuple[str,str]]]:
    """
    Returns: (documents_count, chunks_count, chunk_payloads=[(chunk_id, content)])
    """
    docs = 0
    chunks_total = 0
    chunk_payloads: list[tuple[str,str]] = []

    for doc_id, source, title, md in items:
        text = md.pop("text")
        upsert_document(doc_id, source, title, md)
        docs += 1
        chunks = split_text(text)
        chunk_ids = insert_chunks(doc_id, chunks, {"title": title, **md})
        chunks_total += len(chunk_ids)
        chunk_payloads.extend(list(zip(chunk_ids, chunks)))
        log_event("ingest.document", document_id=doc_id, source=source, title=title, chunks=len(chunk_ids))

    return docs, chunks_total, chunk_payloads
