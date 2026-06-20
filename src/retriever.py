from typing import List, Dict, Any
from src.embedder import Embedder
from src.vector_store import VectorStore

class Retriever:
    def __init__(self, embedder: Embedder, vector_store: VectorStore):
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Embed query and find top-k relevant chunks from vector store.
        """
        # Embed the search query
        query_embedding = self.embedder.embed_query(query)
        
        # Query the vector database
        results = self.vector_store.query(query_embedding, top_k=top_k)
        return results
