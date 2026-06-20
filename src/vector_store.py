import chromadb
from pathlib import Path
from typing import List, Dict, Any, Tuple
from src.chunking import Chunk

class VectorStore:
    def __init__(self, persist_dir: Path):
        self.persist_dir = persist_dir
        self.persist_dir.parent.mkdir(parents=True, exist_ok=True)
        # Initialize chromadb persistent client
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection_name = "documents"
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"} # cosine similarity
        )

    def add_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]):
        """
        Add text chunks and their corresponding embeddings to ChromaDB.
        """
        if not chunks:
            return

        ids = [f"{chunk.source}_p{chunk.page}_c{chunk.chunk_index}" for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]

        # ChromaDB allows adding by batch, it handles batch logic internally,
        # but we can add all since all embeddings are already computed.
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        print(f"Successfully added {len(chunks)} chunks to vector database.")

    def count(self) -> int:
        """Return the number of vectors in the collection."""
        return self.collection.count()

    def delete_collection(self):
        """Delete the collection to allow complete re-indexing."""
        try:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print("Collection deleted and re-created.")
        except Exception as e:
            print(f"Error resetting collection: {e}")

    def query(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for top_k most similar vectors in the collection.
        Returns a list of dicts with keys: 'text', 'source', 'page', 'score'
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        formatted_results = []
        if not results or not results['documents'] or len(results['documents'][0]) == 0:
            return formatted_results

        # Extract values
        docs = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]  # chroma hnsw returns distance

        for doc, meta, dist in zip(docs, metadatas, distances):
            # Calculate similarity score: cosine distance is 1 - similarity, so similarity = 1 - distance
            similarity = 1.0 - dist
            formatted_results.append({
                "text": doc,
                "source": meta.get("source", "Unknown"),
                "page": meta.get("page", 1),
                "score": float(similarity)
            })

        return formatted_results
