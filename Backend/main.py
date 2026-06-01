# =============================================================================
# main.py — FastAPI Application Entry Point
# =============================================================================
# This is the first file that runs when you start the server.
# It sets up the API, initializes all services on startup,
# and defines the available HTTP routes/endpoints.
# =============================================================================

import sys, os
_root = os.path.dirname(os.path.abspath(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()


from models.schemas import ChatRequest, ChatResponse
from services.rag_pipeline import RAGPipeline

# Global pipeline instance — initialized once at startup
pipeline: RAGPipeline = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager:
    - Runs BEFORE the server starts accepting requests (startup)
    - Runs AFTER the server stops (shutdown)

    We initialize the RAG pipeline here so it's ready for every request
    without re-loading or re-connecting on each call.
    """
    global pipeline
    print("=" * 60)
    print("  Student Guide Assistant — Starting Up")
    print("=" * 60)
    pipeline = RAGPipeline()   # Connect to Pinecone + load embedding model
    print("[main] Pipeline ready. Server accepting requests.\n")
    print("[main] Frontend: http://localhost:5173")
    print("[main] API Docs:  http://127.0.0.1:8000/docs")
    yield                       # <-- server is live between here and below
    print("[main] Shutting down gracefully.")


# ── App Initialization ────────────────────────────────────────────────────────
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







# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    """Quick health check to verify the API is running."""
    return {
        "status": "ok",
        "message": "Student Guide Assistant v2 is running.",
        "docs": "/docs"
    }


@app.post("/chat", response_model=ChatResponse, tags=["RAG"])
def chat(request: ChatRequest):
    """
    Core RAG endpoint.

    Flow:
    1. Receive student question
    2. Embed the question using OpenAI
    3. Search Pinecone for the most relevant knowledge chunks
    4. Send question + retrieved context to Claude LLM
    5. Return the grounded answer + the source chunks used

    **Body:** `{ "question": "How do I register for courses?" }`
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    response = pipeline.run(request.question.strip())
    return response


@app.get("/topics", tags=["Knowledge Base"])
def list_topics():
    """
    Returns the list of topics currently indexed in Pinecone.
    Useful for debugging or building a UI dropdown.
    """
    topics = pipeline.get_indexed_topics()
    return {"total": len(topics), "topics": topics}
