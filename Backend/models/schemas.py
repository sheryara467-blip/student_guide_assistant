# models/schemas.py
# Defines the structure of API request and response data using Pydantic

from pydantic import BaseModel
from typing import List


class ChatRequest(BaseModel):
    """Schema for incoming chat requests from the student."""
    question: str  # The student's question


class RetrievedChunk(BaseModel):
    """Represents a single retrieved knowledge chunk with its similarity score."""
    topic: str
    content: str
    score: float  # Cosine similarity score (0 to 1)


class ChatResponse(BaseModel):
    """Schema for the API response returned to the student."""
    question: str                        # Echo back the original question
    answer: str                          # The AI-generated answer
    retrieved_context: List[RetrievedChunk]  # What data was used to generate the answer