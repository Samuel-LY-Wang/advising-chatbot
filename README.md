# Academic Advising Chatbot (RAG)

This project builds an academic advising chatbot for UMass Amherst.
It uses a Retrieval-Augmented Generation (RAG) pipeline to answer questions about course prerequisites, degree requirements, and academic policies.

## Architecture

- **Data collection:** `pipelines/bulk_sources_crawler.py`
- **Chunking:** `pipelines/save_chunks.py`
- **Embedding & Indexing:** `pipelines/save_chunks_to_db.py` (local SentenceTransformers)
- **Retrieval:** `rag/query_data.py` (two-step with k=40, top 5 kept after rerank)
- **Web Interface:** `apps/api/main.py` (FastAPI web UI)


## Setup

(with uv) \
```bash
uv venv --python 3.9
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Local LLM Integration
This project uses Ollama to run AI models locally. \\
For embeddings:
- Install Ollama (OS-dependent)
- For text embedding:
- ```bash
ollama pull bge-m3
```
- For the reranker:
- ```bash
ollama pull qllama/bge-reranker-v2-m3
```
- To test, we use a more lightweight model:
- ```bash
ollama pull qwen3.5:4b
```
- Deployment uses the more powerful qwen3.5:27b model:
- ```bash
ollama pull qwen3.5:27b
```

## How to add additional sources
First, add the link to the "sources" part of config.json \\
Then, simply run pipelines/rebuild_database.py

## Next steps:
Attempting to get ollama installed and a server running on Unity cluster \\
Have inline citations (current approach has end-of-text citations, not all of which are used) \\
Migrate the entire thing to Unity (w/ improvements like recursive depth 2 on links, and perhaps upgrade from qwen3.5:9b to qwen3.5:27b)