from fastapi import FastAPI, Query, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import json
import numpy as np
from pathlib import Path
from rag.query_data import answer_query as answer
from pipelines import rebuild_database, Util
import uvicorn
import traceback

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama

import logging
logging.getLogger("pypdf").setLevel(logging.ERROR)

app = FastAPI(title="Advising Chatbot RAG API")
templates = Jinja2Templates(directory="apps/api/templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/ask")
def ask(q: str = Query(..., description="Your question")):
    ans = Util.time_execution(lambda: answer(q))
    print(ans)
    ans, sources = ans # Just see how long each query takes on laptop
    print(ans)
    return {"question": q, "answer": str(ans), "sources": sources}

@app.post("/rebuild_db")
def rebuild_db(request: Request):
    api_key = request.headers.get("api-key")
    expected_key = os.getenv("REBUILD_API_KEY")
    if api_key != expected_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key.")
    try:
        rebuild_database.main()
        return {"status": "success", "message": "Database rebuilt successfully."}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)