CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
  id           TEXT PRIMARY KEY,
  source       TEXT NOT NULL,
  title        TEXT,
  metadata     JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunks (
  id           TEXT PRIMARY KEY,
  document_id  TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index  INT NOT NULL,
  content      TEXT NOT NULL,
  metadata     JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- 384 dims matches "all-MiniLM-L6-v2"
CREATE TABLE IF NOT EXISTS embeddings (
  chunk_id     TEXT PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE,
  embedding    vector(768) NOT NULL
);

-- Vector index
CREATE INDEX IF NOT EXISTS idx_embeddings_ivfflat
ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Helpful filter indexes
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_documents_source ON documents(source);
