# services/llm_service.py
# Responsible for generating a final answer using an LLM (Groq API).
# The retrieved context is injected into the prompt so the answer is grounded in real data.

import os
from groq import Groq
from typing import List, Dict


class LLMService:
    """
    Uses the Groq API to generate answers based on retrieved context.
    This is the "Generation" step in the RAG pipeline.
    """
    MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Missing GROQ_API_KEY in .env")

        self.client = Groq(api_key=api_key)
        self.model = self.MODEL

    def generate_answer(self, question: str, context_chunks: List[Dict]) -> str:
        """
        Generates a helpful answer by combining the student's question
        with the most relevant retrieved knowledge.

        Args:
            question:       The student's original question.
            context_chunks: List of retrieved knowledge entries with topic + content.

        Returns:
            A string containing the AI-generated answer.
        """

        # Step 1: Format retrieved chunks into a readable context block
        context_text = self._format_context(context_chunks)

        # Step 2: Build the prompt — instruct the model to use ONLY the provided context
        prompt = f"""You are a helpful Student Guide Assistant at a university.
Your job is to answer student questions clearly and accurately.

Use ONLY the information provided in the context below to answer the question.
If the context does not contain enough information, say so honestly.
Do not make up facts. Keep your answer concise and student-friendly.

--- RETRIEVED CONTEXT ---
{context_text}
--- END OF CONTEXT ---

Student's Question: {question}

Answer:"""

        # Step 3: Call the Groq Chat Completions API
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a concise, accurate student guide assistant.",
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1024,
        )

        # Step 4: Extract and return the text response
        answer = completion.choices[0].message.content
        print(f"[LLMService] Generated answer ({len(answer)} chars).")
        return answer

    def _format_context(self, chunks: List[Dict]) -> str:
        """
        Formats retrieved knowledge chunks into a structured string for the prompt.

        Args:
            chunks: List of retrieved documents.

        Returns:
            A formatted multi-line string of topics and their content.
        """
        formatted = []
        for i, chunk in enumerate(chunks, start=1):
            topic = chunk.get("topic", "General")
            content = chunk.get("content", "")
            score = chunk.get("score", 0.0)
            formatted.append(
                f"[{i}] Topic: {topic}\n"
                f"    Content: {content}\n"
                f"    Relevance Score: {score}"
            )
        return "\n\n".join(formatted)
