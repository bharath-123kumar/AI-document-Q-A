import torch
from sentence_transformers import SentenceTransformer

model_name = "sentence-transformers/all-MiniLM-L6-v2"
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

try:
    print("Attempting to load model on default device...")
    model = SentenceTransformer(model_name)
    print("Success loading model on default device!")
    
    # Try embedding a test sentence
    emb = model.encode("Hello world")
    print(f"Embedding shape: {emb.shape}")
except Exception as e:
    print(f"Error on default: {e}")

try:
    print("\nAttempting to load model with explicit device...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    model_explicit = SentenceTransformer(model_name, device=device)
    print("Success loading model with explicit device!")
    emb = model_explicit.encode("Hello world")
    print(f"Embedding shape: {emb.shape}")
except Exception as e:
    print(f"Error on explicit device: {e}")
