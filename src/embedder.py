from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        # Lazy loading to speed up CLI imports if not initialized immediately
        self.model = None

    def _load_model(self):
        if self.model is None:
            import torch
            
            # Determine the best available hardware accelerator device
            if torch.cuda.is_available():
                device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
                
            print(f"Loading embedding model: {self.model_name} on device: {device}...")
            
            # Prevent NotImplementedError by disabling low_cpu_mem_usage.
            # This prevents transformers/accelerate from initializing the model on the 'meta' device,
            # loading the model parameters directly into the designated target device.
            model_kwargs = {"low_cpu_mem_usage": False}
            
            try:
                self.model = SentenceTransformer(
                    self.model_name,
                    device=device,
                    model_kwargs=model_kwargs
                )
            except TypeError:
                # Fallback: if sentence-transformers version is < 3.0, model_kwargs might not be supported.
                print(f"model_kwargs parameter not supported. Falling back to default device loading on {device}...")
                self.model = SentenceTransformer(self.model_name, device=device)

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Embed a list of texts in batches to comply with assignment guidelines.
        """
        self._load_model()
        # Encode returns a numpy array or list of embeddings
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        # Convert numpy embeddings to list of floats for ChromaDB compatibility
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query string.
        """
        self._load_model()
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
