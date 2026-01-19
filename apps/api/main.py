from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import json
import numpy as np
from pathlib import Path
from rag.query_data import answer_query as answer
from pipelines import bulk_sources_crawler, save_chunks, save_chunks_to_db
import uvicorn

app = FastAPI(title="Advising Chatbot RAG API")
templates = Jinja2Templates(directory="apps/api/templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/ask")
def ask(q: str = Query(..., description="Your question")):
    ans = answer(q)
    return {"question": q, "answer": ans}

@app.get("/rebuild_embeddings")
def rebuild_embeddings(request: Request):
    api_key = request.headers.get("x-api-key")
    expected_key = os.getenv("REBUILD_API_KEY")
    if api_key != expected_key:
        return {"status": "error", "message": "API Key is missing or invalid."}

    try:
        bulk_sources_crawler.fetch_all()
        save_chunks.generate_data_store()
        chunks = save_chunks_to_db.load_chunks()
        save_chunks_to_db.save_to_chroma(chunks)
        return {"status": "success", "message": "Embeddings rebuilt successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)