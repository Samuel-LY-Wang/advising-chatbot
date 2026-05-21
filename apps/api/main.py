from fastapi import FastAPI, Query, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from rag.query_data import answer_query as answer
from pipelines import rebuild_database, Util
import URL_utils
import uvicorn
import traceback
import markdown

import logging
logging.getLogger("pypdf").setLevel(logging.ERROR)

#TODO: change API package from FastAPI to the slurm one (deploy to Unity cluster)

app = FastAPI(title="Advising Chatbot RAG API")
templates = Jinja2Templates(directory="apps/api/templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/ask")
def ask(q: str = Query(..., description="Your question")):
    logging.info("Received question: %s", q)
    ans, sources = Util.time_execution(lambda: answer(q, debug=False), out="Answer time: ")
    logging.info("Generated answer: %s", ans)
    source_links = [URL_utils.to_html_link(url, str(i+1)) for i, url in enumerate(sources)]
    return {"question": q, "answer": markdown.markdown(ans), "sources": source_links}

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
        logging.error("Error rebuilding database: %s", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)