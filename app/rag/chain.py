from __future__ import annotations
from dataclasses import dataclass
from app.config import settings
from app.rag.prompts import SYSTEM_RAG, USER_RAG

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama

@dataclass
class LLMResult:
    text: str

def get_llm():
    if settings.LLM_PROVIDER == "ollama":
        return ChatOllama(model="mistral", temperature=0.2)
    if settings.LLM_PROVIDER == "openai":
        return ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0.2)
    # mock LLM for offline run: just returns the context-trimmed template
    return None

def render_answer(question: str, context: str) -> LLMResult:
    llm = get_llm()
    if llm is None:
        # Offline fallback so the repo still "works" without keys:
        text = (
            "OFFLINE MODE (no LLM). Here is the retrieved context you should use to answer:\n\n"
            + context[:4000]
        )
        return LLMResult(text=text)

    msgs = [
        SystemMessage(content=SYSTEM_RAG),
        HumanMessage(content=USER_RAG.format(question=question, context=context)),
    ]
    out = llm.invoke(msgs)
    return LLMResult(text=out.content)
