import os
from typing import List, Tuple
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from rag_core import build_rag_chain

load_dotenv()
app = FastAPI(title="DUPR RAG API")
rag_chain = None

class ChatRequest(BaseModel):
    message: str
    history: List[Tuple[str, str]] = []  # [(user, assistant), ...]

def startup():
    global rag_chain
    if rag_chain is None:
        rag_chain = build_rag_chain()

@app.on_event("startup")
def on_start():
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("Missing GROQ_API_KEY")
    startup()

@app.post("/chat")
def chat(req: ChatRequest):
    lc_history = []
    for user, bot in req.history:
        if user:
            lc_history.append(HumanMessage(content=user))
        if bot:
            lc_history.append(AIMessage(content=bot))
    resp = rag_chain.invoke({"input": req.message, "chat_history": lc_history})
    return {"answer": resp["answer"]}
