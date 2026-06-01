# services/retrieval_service.py
# Handles searching the knowledge base to find the most relevant documents
# for a given student question using cosine similarity.

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Optional

from services.embedding_service import EmbeddingService
from services.pinecone_service import PineconeService


class RetrievalService:
    """
    Retrieves the top-K most relevant knowledge chunks for a given query.
    Uses cosine similarity between the query vector and document vectors.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        pinecone_service: Optional[PineconeService] = None,
    ):
        # We depend on the embedding service to convert text to vectors
        self.embedding_service = embedding_service
        self.pinecone_service = pinecone_service

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Finds the most relevant documents for the given query.

        Args:
            query:  The student's question.
            top_k:  Number of top results to return (default: 3).

        Returns:
            A list of the top_k most relevant documents, each with a 'score' field added.
        """
        # Step 1: Convert the query into a vector
        query_vector = self.embedding_service.embed_query(query)

        if self.pinecone_service is not None:
            results = self.pinecone_service.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
            )

            matches = results.get("matches", []) if isinstance(results, dict) else results.matches
            retrieved = []
            for match in matches:
                if isinstance(match, dict):
                    metadata = dict(match.get("metadata") or {})
                    metadata["score"] = float(round(match.get("score", 0.0), 4))
                else:
                    metadata = dict(match.metadata or {})
                    metadata["score"] = float(round(match.score or 0.0, 4))
                if not retrieved:
                    print(f"[RetrievalService] First match metadata keys: {list(metadata.keys())}")
                metadata.setdefault("topic", "General")
                metadata["content"] = (
                    metadata.get("content")
                    or metadata.get("text")
                    or metadata.get("chunk_text")
                    or metadata.get("page_content")
                    or metadata.get("document")
                    or metadata.get("body")
                    or ""
                )
                metadata.setdefault("source", "")
                retrieved.append(metadata)

            print(f"[RetrievalService] Retrieved {len(retrieved)} chunks for query: '{query[:60]}...'")
            return retrieved

        # Step 2: Get all pre-computed document vectors
        doc_vectors = self.embedding_service.get_document_vectors()

        # Step 3: Compute cosine similarity between query and every document
        # cosine_similarity returns a 2D array — we take the first row (our single query)
        similarities = cosine_similarity(query_vector, doc_vectors)[0]

        # Step 4: Sort by score (descending) and pick the top_k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # Step 5: Build result list with scores attached
        results = []
        for idx in top_indices:
            doc = self.embedding_service.documents[idx].copy()
            doc["score"] = float(round(similarities[idx], 4))
            results.append(doc)

        print(f"[RetrievalService] Retrieved {len(results)} chunks for query: '{query[:60]}...'")
        return results
