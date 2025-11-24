# RAG-QA-K8s: Production-Grade Retrieval-Augmented Generation on Kubernetes

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-UVicorn-green)
![Kubernetes](https://img.shields.io/badge/K8s-Minikube%20%2B%20HPA-orange)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

Fully local, private, auto-scaling RAG system – exactly the architecture used at Booking.com, ING, Philips, and other Dutch tech giants.

## Features
- Upload any PDF (research papers, internal docs, contracts)
- Automatic chunking + embedding with `sentence-transformers/all-MiniLM-L6-v2`
- Persistent FAISS vector store
- Ask questions → retrieves exact chunks → answers with citations via local Ollama LLM
- Production-ready FastAPI backend
- Dockerized & deployed on Minikube
- Horizontal Pod Autoscaler (HPA) – real auto-scaling based on CPU
- 100% local – zero API keys, zero cloud costs, full privacy

## Tech Stack
- FastAPI + Uvicorn
- LangChain
- Ollama (Llama 3.2 / Gemma 2 / Phi-3 – your choice)
- FAISS (CPU-optimized)
- sentence-transformers/all-MiniLM-L6-v2
- Minikube + Kubernetes HPA
- Docker

## Quick Start (Mac/Linux)
```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Run Ollama (separate terminal)
ollama serve & ollama pull llama3.2

# Build & deploy
docker build -t rag-qa-k8s:latest .
kubectl apply -f k8s/



## Live Demo :

minikube tunnel
Go to http://127.0.0.1:8000/docs
Upload a PDF → ask questions → watch citations appear


## Project Structure
rag-qa-k8s/
├── app/                  # FastAPI code
├── data/                 # uploaded PDFs
├── vector_store/         # FAISS index
├── k8s/                  # Kubernetes manifests + HPA
├── Dockerfile
├── requirements.txt
└── README.md