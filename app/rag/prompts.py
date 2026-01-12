SYSTEM_RAG = """You are a senior software engineer assistant.
Answer using ONLY the provided context. If the context is insufficient, say so and ask for the missing detail.
Always include bullet-point citations in the answer as [doc_id:chunk_id]."""

USER_RAG = """Question:
{question}

Context (chunks):
{context}

Write a concise, correct answer with citations."""
