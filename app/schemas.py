from pydantic import BaseModel
from typing import List, Optional

class UploadResponse(BaseModel):
    filename: str
    chunks_added: int
    total_chunks_in_store: int
    message: str = "PDF processed and added to knowledge base successfully!"

class ChatMessage(BaseModel):
    question: str

class Citation(BaseModel):
    content: str
    source_pdf: str
    chunk_id: int
    page_number: Optional[int] = None

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    model_used: str = "llama3.2 (via Ollama)"

    class Config:
        json_encoders = {
            # Helps with serializing any weird objects if they sneak in
        }
