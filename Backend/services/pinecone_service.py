import os
from pinecone import Pinecone


class PineconeService:
    def __init__(self):
        api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX_NAME")

        if not api_key:
            raise ValueError("Missing PINECONE_API_KEY in .env")
        if not index_name:
            raise ValueError("Missing PINECONE_INDEX_NAME in .env")

        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)

    def upsert(self, vectors, namespace=None):
        return self.index.upsert(vectors=vectors, namespace=namespace)

    def query(self, vector, top_k=5, namespace=None, include_metadata=True):
        return self.index.query(
            vector=vector,
            top_k=top_k,
            namespace=namespace,
            include_metadata=include_metadata,
        )

    def get_index_stats(self):
        stats = self.index.describe_index_stats()
        if isinstance(stats, dict):
            return stats
        return {
            "total_vector_count": stats.total_vector_count,
            "namespaces": stats.namespaces,
        }

    def list_metadata_values(self, field, namespace=None):
        stats = self.get_index_stats()
        namespaces = stats.get("namespaces", {})

        if not namespaces:
            return []

        query_namespace = namespace or next(iter(namespaces.keys()), None)
        if query_namespace is None:
            return []

        # Pinecone does not provide a direct "distinct metadata values" endpoint.
        # Return an empty list until the app stores this list separately.
        return []