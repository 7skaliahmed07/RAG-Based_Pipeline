import os
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

VECTOR_STORE_PATH = Path(os.getenv("VECTOR_STORE_PATH", "./vector_store"))
VECTOR_STORE_PATH.mkdir(exist_ok=True)

def get_vector_store():
    if (VECTOR_STORE_PATH / "index.faiss").exists():
        return FAISS.load_local(
            folder_path=str(VECTOR_STORE_PATH),
            embeddings=embeddings,
            index_name="index",
            allow_dangerous_deserialization=True
        )
    
    # Create truly empty store
    db = FAISS.from_texts(["init"], embeddings)
    db.save_local(str(VECTOR_STORE_PATH), index_name="index")
    db.delete(ids=db.index_to_docstore_id.values())
    db.save_local(str(VECTOR_STORE_PATH), index_name="index")
    return db

def add_documents_to_vector_store(chunks):
    db = get_vector_store()
    db.add_documents(chunks)
    db.save_local(str(VECTOR_STORE_PATH), index_name="index")
    print(f"Added {len(chunks)} chunks → total: {db.index.ntotal}")

def retrieve_relevant_chunks(query: str, k: int = 4):
    db = get_vector_store()
    if db.index.ntotal == 0:
        return []
    retriever = db.as_retriever(search_kwargs={"k": min(k, db.index.ntotal)})
    return retriever.invoke(query)
