import os
import sys
from pathlib import Path
from src.utils import get_data_dir, get_chroma_dir
from src.ingestion import load_documents_from_folder
from src.chunking import split_documents
from src.embedder import Embedder
from src.vector_store import VectorStore

def main():
    print("=" * 60)
    print("RAG Document Indexing Pipeline")
    print("=" * 60)

    # 1. Setup paths
    data_dir = get_data_dir()
    chroma_dir = get_chroma_dir()

    print(f"Data directory: {data_dir.absolute()}")
    print(f"Vector Database directory: {chroma_dir.absolute()}")

    # Check if data directory is empty
    if not any(data_dir.iterdir()):
        print(f"\nWARNING: No documents found in {data_dir}.")
        print("Please run 'python generate_data_files.py' to generate sample documents first.")
        sys.exit(1)

    # 2. Load documents
    print("\nStep 1: Loading documents from data folder...")
    documents = load_documents_from_folder(data_dir)
    if not documents:
        print("No valid text could be extracted from the documents. Exiting.")
        sys.exit(1)
    print(f"Loaded {len(documents)} document pages/sections.")

    # 3. Chunk documents
    print("\nStep 2: Splitting documents into semantic chunks...")
    # Using 800 token chunk size, 150 token overlap
    chunks = split_documents(documents, chunk_size=800, chunk_overlap=150)
    print(f"Created {len(chunks)} text chunks.")

    # 4. Generate embeddings
    print("\nStep 3: Generating embeddings (batched encode)...")
    embedder = Embedder()
    # Extract chunk texts
    chunk_texts = [chunk.text for chunk in chunks]
    # Perform batched embedding (runs inside embedder)
    embeddings = embedder.embed_texts(chunk_texts, batch_size=32)
    print(f"Generated {len(embeddings)} embeddings.")

    # 5. Store in ChromaDB
    print("\nStep 4: Storing embeddings and metadata in ChromaDB...")
    vector_store = VectorStore(chroma_dir)
    
    # Reset collection first to ensure a clean run
    vector_store.delete_collection()
    
    # Store
    vector_store.add_chunks(chunks, embeddings)

    print("\n" + "=" * 60)
    print(f"Indexing completed successfully!")
    print(f"Total vectors stored: {vector_store.count()}")
    print("=" * 60)

if __name__ == "__main__":
    main()
