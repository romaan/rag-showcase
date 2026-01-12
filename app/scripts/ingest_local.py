from __future__ import annotations
import argparse
from app.db.pg import run_sql_file
from app.rag.ingest import ingest_local_dir, persist_docs_and_chunks
from app.rag.vectorize import embed_texts, upsert_embeddings

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default="./data/docs")
    ap.add_argument("--migrate-only", action="store_true")
    args = ap.parse_args()

    run_sql_file("app/db/migrations/001_init.sql")
    if args.migrate_only:
        print("Migrated.")
        return

    _, _, items = ingest_local_dir(args.path)
    docs, chunks, chunk_payloads = persist_docs_and_chunks(items)

    chunk_ids = [cid for cid, _ in chunk_payloads]
    texts = [t for _, t in chunk_payloads]
    vectors = embed_texts(texts)
    upsert_embeddings(chunk_ids, vectors)

    print(f"Ingested documents={docs}, chunks={chunks}")

if __name__ == "__main__":
    main()
