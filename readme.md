# RAG Showcase (FastAPI + LangChain + pgvector + Ollama)

This repository demonstrates an end-to-end Retrieval Augmented Generation (RAG) pipeline:
- Knowledge connectors: local docs (txt/md/pdf) and web URLs
- Chunking strategy: recursive splitter with overlap
- Embeddings: local SentenceTransformers (default) or OpenAI embeddings
- Vector store: Postgres + pgvector (cosine distance + ivfflat index)
- Retrieval: top-k semantic search (+ optional source filter)
- Generation: LangChain Chat model (OpenAI) or offline mock mode
- Agent demo: a lightweight tool-calling endpoint

## Quickstart

Run Ollama in a terminal

```bash
ollama serve
ollama pull mistral
ollama pull nomic-embed-text
ollama list

# Quick test
curl http://localhost:11434/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model":"nomic-embed-text","prompt":"test"}' | python -c \
"import sys, json; print(len(json.load(sys.stdin)['embedding']))"

```


```bash
# from rag-showcase/
cp .env.example .env
docker compose up -d

poetry install

mkdir -p data/docs
# Place some text files inside this folder


# add some docs into ./data/docs (txt/md/pdf)
poetry run python -m app.scripts.ingest_local --path ./data/docs


poetry run python -c "import app; print('ok')"
poetry run uvicorn app.main:app --reload --port 8000

# test
curl -s http://localhost:8000/health
curl -s http://localhost:8000/ask \
  -H 'content-type: application/json' \
  -d '{"question":"Summarize what these docs say about authentication.", "top_k": 5}'
```
