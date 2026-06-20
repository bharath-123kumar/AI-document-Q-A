from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.ingestion import Document

# We will define a Chunk class to keep things structured
class Chunk:
    def __init__(self, text: str, source: str, page: int, chunk_index: int):
        self.text = text
        self.source = source
        self.page = page
        self.chunk_index = chunk_index
        self.metadata = {
            "source": source,
            "page": page,
            "chunk_index": chunk_index
        }

    def __repr__(self):
        return f"Chunk(source={self.source}, page={self.page}, index={self.chunk_index}, length={len(self.text)})"

def split_documents(documents: List[Document], chunk_size: int = 800, chunk_overlap: int = 150) -> List[Chunk]:
    """
    Split the input documents into smaller chunks using the RecursiveCharacterTextSplitter.
    This strategy tries to keep paragraphs and sentences together.
    """
    # Initialize the splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = []
    for doc in documents:
        # Split text for this specific document page
        split_texts = splitter.split_text(doc.text)
        for i, text in enumerate(split_texts):
            chunks.append(
                Chunk(
                    text=text,
                    source=doc.source,
                    page=doc.page,
                    chunk_index=i
                )
            )
    return chunks
