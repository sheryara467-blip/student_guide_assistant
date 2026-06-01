# services/embedding_service.py
# Converts user questions into the same dense vectors used for Pinecone ingestion.

# from sentence_transformers import SentenceTransformer


# class EmbeddingService:
#     """
#     Uses the local all-MiniLM-L6-v2 model.
#     This must match the model used when uploading vectors to Pinecone.
#     """

#     def __init__(self):
#         print("[EmbeddingService] Loading local embedding model...")
#         self.model = SentenceTransformer("all-MiniLM-L6-v2")
#         print("[EmbeddingService] Embedding model ready.")

#     def embed_query(self, query: str):
#         return self.model.encode(query).tolist()






# services/embedding_service.py
from fastembed import TextEmbedding

class EmbeddingService:
    def __init__(self):
        print("[EmbeddingService] Loading embedding model...")
        self.model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        print("[EmbeddingService] Embedding model ready.")

    def embed_query(self, query: str):
        embeddings = list(self.model.embed([query]))
        return embeddings[0].tolist()