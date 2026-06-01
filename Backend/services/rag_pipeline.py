# services/rag_pipeline.py
import sys, os
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from typing import List
from models.schemas import ChatResponse, RetrievedChunk
from services.embedding_service import EmbeddingService
from services.pinecone_service import PineconeService
from services.retrieval_service import RetrievalService
from services.llm_service import LLMService


class RAGPipeline:
    def __init__(self):
        print("[RAGPipeline] Initializing all services...")

        self.embedding_service = EmbeddingService()
        self.pinecone_service  = PineconeService()
        self.retrieval_service = RetrievalService(
            self.embedding_service,
            self.pinecone_service
        )
        self.llm_service = LLMService()

        # Verify Pinecone index has data
        stats = self.pinecone_service.get_index_stats()
        total = stats.get("total_vector_count", 0)
        print(f"[RAGPipeline] Pinecone index has {total} vectors.")
        print("[RAGPipeline] All services ready.\n")

    def run(self, question: str) -> ChatResponse:
        print(f"\n[RAGPipeline] Question: '{question}'")

        # Retrieve top-3 relevant chunks from Pinecone
        retrieved_chunks = self.retrieval_service.retrieve(question, top_k=3)

        if not retrieved_chunks:
            return ChatResponse(
                question=question,
                answer="I couldn't find relevant information. Please contact student services.",
                retrieved_context=[],
                model_used=LLMService.MODEL
            )

        # Generate answer using Claude
        answer = self.llm_service.generate_answer(question, retrieved_chunks)

        context_for_response = [
            RetrievedChunk(
                topic=chunk["topic"],
                content=chunk["content"],
                score=chunk["score"],
                source=chunk.get("source", "")
            )
            for chunk in retrieved_chunks
        ]

        return ChatResponse(
            question=question,
            answer=answer,
            retrieved_context=context_for_response,
            model_used=LLMService.MODEL
        )

    def get_indexed_topics(self) -> List[str]:
        return self.pinecone_service.list_metadata_values(field="topic")