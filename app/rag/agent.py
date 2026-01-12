from __future__ import annotations
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

from app.config import settings
from app.rag.chain import render_answer
from app.logging import log_event

@tool
def answer_with_rag(question: str) -> str:
    """Answer a question using the RAG pipeline."""
    # In the API route we already do retrieval; this is here to demonstrate agent tooling.
    return render_answer(question, context="(agent tool demo: call /ask for full retrieval)").text

def run_agent(user_question: str) -> str:
    if settings.LLM_PROVIDER != "openai":
        return "Agent requires OPENAI (set LLM_PROVIDER=openai). Use /ask without agent."

    llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0.2)
    llm_tools = llm.bind_tools([answer_with_rag])

    system = SystemMessage(content="You are an agent. Decide when to call tools. Keep answers short.")
    user = HumanMessage(content=user_question)

    msg = llm_tools.invoke([system, user])
    log_event("agent.invoked", tool_calls=getattr(msg, "tool_calls", None))

    # If the model requested tool calls, run them once (simple single-iteration agent loop)
    if getattr(msg, "tool_calls", None):
        for tc in msg.tool_calls:
            if tc["name"] == "answer_with_rag":
                tool_out = answer_with_rag.invoke(tc["args"])
                return tool_out
    return msg.content
