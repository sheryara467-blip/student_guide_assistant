import sys, os
_root = os.path.dirname(os.path.abspath(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware      # ← ADD
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from models.schemas import ChatRequest, ChatResponse
from services.rag_pipeline import RAGPipeline

pipeline: RAGPipeline = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline
    print("=" * 60)
    print("  Student Guide Assistant — Starting Up")
    print("=" * 60)
    pipeline = RAGPipeline()
    print("[main] Pipeline ready. Server accepting requests.\n")
    print("[main] Frontend: http://localhost:5173")
    print("[main] API Docs:  http://127.0.0.1:8000/docs")
    yield
    print("[main] Shutting down gracefully.")

app = FastAPI(
    title="Student Guide Assistant API",
    description="""
A **Retrieval-Augmented Generation (RAG)** backend that answers student questions
by searching a Pinecone vector database (populated from university PDF documents)
and generating grounded answers via the Claude LLM.

## Endpoints
- `GET  /`        — Health check
- `POST /chat`    — Ask a student question, get a RAG-powered answer
- `GET  /topics`  — List all topics stored in the knowledge base
""",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(                                     # ← ADD
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://student-guide-assistant.vercel.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "message": "Student Guide Assistant v2 is running.",
        "docs": "/docs"
    }

@app.post("/chat", response_model=ChatResponse, tags=["RAG"])
def chat(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    response = pipeline.run(request.question.strip())
    return response

@app.get("/topics", tags=["Knowledge Base"])
def list_topics():
    topics = pipeline.get_indexed_topics()
    return {"total": len(topics), "topics": topics}