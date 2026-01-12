from __future__ import annotations
from fastapi import FastAPI, HTTPException
from app.config import settings
from app.logging import setup_logging, log_event
from app.db.pg import run_sql_file

from app.rag.models import AskRequest, AskResponse, Citation
from app.rag.vectorize import embed_texts
from app.rag.retriever import vector_search
from app.rag.chain import render_answer
from app.rag.agent import run_agent

setup_logging()

app = FastAPI(title="RAG Showcase", version="0.1.0")

@app.on_event("startup")
def startup():
    # safe to run repeatedly
    run_sql_file("app/db/migrations/001_init.sql")
    log_event("app.start", env=settings.APP_ENV)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question is required")

    top_k = req.top_k or settings.TOP_K

    q_vec = embed_texts([req.question])[0]
    rows = vector_search(q_vec, top_k=top_k, filter_source=req.filter_source)

    context_lines = []
    citations: list[Citation] = []
    for r in rows:
        chunk_id = r["chunk_id"]
        doc_id = r["document_id"]
        score = float(r["score"])
        content = r["content"]
        title = r.get("title")
        source = r.get("source")

        context_lines.append(f"[{doc_id}:{chunk_id}] {content}")
        citations.append(Citation(
            document_id=doc_id,
            title=title,
            source=source,
            chunk_id=chunk_id,
            score=score,
            snippet=content[:240] + ("..." if len(content) > 240 else "")
        ))

    context = "\n\n".join(context_lines) if context_lines else "(no context retrieved)"
    llm_res = render_answer(req.question, context=context)

    return AskResponse(
        answer=llm_res.text,
        citations=citations,
        used_top_k=top_k
    )

@app.post("/agent")
def agent(req: AskRequest):
    # separate endpoint just to show agent/tooling ability
    return {"answer": run_agent(req.question)}
