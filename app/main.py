import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pathlib import Path
import logging

from app.utils.loader import process_pdf
from app.rag import add_documents_to_vector_store, retrieve_relevant_chunks, get_vector_store
from app.schemas import UploadResponse, ChatMessage, ChatResponse, Citation
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG-QA-K8s",
    description="Production-grade local RAG with FAISS + Ollama",
    version="1.0.0"
)

llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "llama3.2"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    temperature=0.2
)

# 100% FIXED – double curly braces everywhere
prompt = PromptTemplate.from_template(
    """You are an expert AI assistant. Answer the question using ONLY the context below.
Be concise, confident, and cite every claim.

Context:
{context}

Question: {question}

Answer and cite using this exact format at the end of relevant sentences:
[Source: attention.pdf, Chunk <number>]

Example: The Transformer replaces recurrence with attention [[Source: attention.pdf, Chunk 0]].
"""
)

chain = prompt | llm | StrOutputParser()

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files allowed")
    
    file_path = DATA_DIR / file.filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    logger.info(f"Processing {file.filename}...")
    chunks = process_pdf(str(file_path))
    
    db = get_vector_store()
    old_count = db.index.ntotal
    add_documents_to_vector_store(chunks)
    
    return UploadResponse(
        filename=file.filename,
        chunks_added=len(chunks),
        total_chunks_in_store=old_count + len(chunks),
        message="PDF processed and added successfully!"
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatMessage):
    docs = retrieve_relevant_chunks(request.question, k=4)
    
    if not docs:
        return ChatResponse(
            answer="No relevant information found.",
            citations=[],
            model_used=os.getenv("OLLAMA_MODEL", "llama3.2")
        )
    
    context = "\n\n".join([
        f"[Chunk {doc.metadata['chunk_id']}] {doc.page_content}"
        for doc in docs
    ])
    
    raw_answer = chain.invoke({"context": context, "question": request.question})
    
    citations = [
        Citation(
            content=doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
            source_pdf=doc.metadata["source_pdf"],
            chunk_id=doc.metadata["chunk_id"],
            page_number=doc.metadata.get("page")
        )
        for doc in docs
    ]
    
    return ChatResponse(answer=raw_answer, citations=citations)

@app.get("/")
async def root():
    return {"message": "RAG-QA-K8s is running! Go to /docs"}
