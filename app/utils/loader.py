from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

def load_pdf(file_path: str):
    """Load PDF and return raw pages"""
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    return pages

def chunk_documents(documents, chunk_size: int = 1000, chunk_overlap: int = 200):
    """Smart chunking – preserves paragraphs, avoids breaking sentences"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

def process_pdf(file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    """One-stop function: PDF → cleaned chunks with metadata"""
    pages = load_pdf(file_path)
    chunks = chunk_documents(pages, chunk_size, chunk_overlap)
    
    # Add source metadata for citations
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
        chunk.metadata["source_pdf"] = os.path.basename(file_path)
    
    return chunks
