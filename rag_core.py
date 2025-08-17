import os
import json
from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.docstore.document import Document
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv

load_dotenv()  # nạp biến môi trường từ .env nếu có

# --- Config qua ENV (có default) ---
TARGET_CLUB_ID = os.getenv("TARGET_CLUB_ID", "5380169465")
SUMMARIES_JSONL = os.getenv("SUMMARIES_JSONL", f"player_summaries_{TARGET_CLUB_ID}.jsonl")
BLOGS_JSONL = os.getenv("BLOGS_JSONL", "blog_posts_detail.jsonl")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "llama3-8b-8192")
PERSIST_DIRECTORY = os.getenv("PERSIST_DIRECTORY", "chroma_db_dupr")

# --- Prompt templates ---
CONTEXTUALIZE_PROMPT_TEMPLATE = """
Given a chat history and the latest user question which might reference context in the chat history,
formulate a standalone question which can be understood without the chat history.
Do NOT answer the question, just reformulate it if needed and otherwise return it as is.

Chat History:
{chat_history}

Follow Up Input:
{input}

Standalone question:
"""

QA_PROMPT_TEMPLATE = """
Bạn là một trợ lý AI chuyên gia về Pickleball và hệ thống xếp hạng DUPR.
Nhiệm vụ của bạn là sử dụng những thông tin trong mục "Context" dưới đây để trả lời câu hỏi của người dùng một cách chính xác, chi tiết và thân thiện.
Nếu thông tin trong Context không đủ để trả lời, hãy trả lời một cách lịch sự rằng bạn không tìm thấy thông tin cụ thể về vấn đề đó. Đừng bịa đặt thông tin.

Context:
{context}

Question:
{input}

Answer:
"""

def _load_jsonl_docs(path: str, build_doc_fn) -> List[Document]:
    docs: List[Document] = []
    if not os.path.exists(path):
        print(f"⚠️  Không tìm thấy file: {path}")
        return docs
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            doc = build_doc_fn(data)
            if doc:
                docs.append(doc)
    return docs

def load_documents() -> List[Document]:
    # Player summaries
    player_docs = _load_jsonl_docs(
        SUMMARIES_JSONL,
        lambda d: Document(
            page_content=(
                f"Tóm tắt người chơi: {d.get('player_name','N/A')}\n"
                f"ID người chơi: {d.get('player_id')}\n"
                f"ID Câu lạc bộ: {d.get('club_id')}\n"
                f"Tổng số trận: {d.get('total_matches')}\n"
                f"Thắng/Thua: {d.get('wins')}/{d.get('losses')}\n"
                f"Thành tích Đơn: {d.get('singles_wins')} thắng - {d.get('singles_losses')} thua\n"
                f"Thành tích Đôi: {d.get('doubles_wins')} thắng - {d.get('doubles_losses')} thua\n"
                f"Tóm tắt chi tiết: {d.get('summary')}"
            ),
            metadata={
                "source": "player_summary",
                "player_id": d.get("player_id"),
                "player_name": d.get("player_name"),
            },
        )
    )

    # Blog posts
    blog_docs = _load_jsonl_docs(
        BLOGS_JSONL,
        lambda d: Document(
            page_content=(
                f"Tiêu đề bài blog: {d.get('title')}\n"
                f"Ngày đăng: {d.get('date')}\n"
                f"Nội dung: {d.get('content')}"
            ),
            metadata={
                "source": "blog",
                "url": d.get("url"),
                "title": d.get("title"),
            },
        )
    )

    docs = player_docs + blog_docs
    print(f"✅ Đã tải {len(player_docs)} tài liệu player + {len(blog_docs)} tài liệu blog (tổng {len(docs)}).")
    return docs

def build_rag_chain():
    docs = load_documents()
    if not docs:
        raise RuntimeError("❌ Không có tài liệu nào để lập chỉ mục. Hãy kiểm tra các file .jsonl.")

    print("⏳ Khởi tạo embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    print("✅ Embeddings OK.")

    print(f"⏳ Tạo/tải ChromaDB tại '{PERSIST_DIRECTORY}'...")
    vector_store = Chroma.from_documents(docs, embeddings, persist_directory=PERSIST_DIRECTORY)
    print("✅ Vector store OK.")

    retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("❌ Thiếu GROQ_API_KEY trong biến môi trường hoặc .env")

    llm = ChatGroq(temperature=0, groq_api_key=api_key, model_name=LLM_MODEL_NAME)

    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", CONTEXTUALIZE_PROMPT_TEMPLATE),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", QA_PROMPT_TEMPLATE),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ])
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    print("✅ RAG chain hội thoại sẵn sàng.")
    return rag_chain
