import shutil
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
import Util

import os
CUR_PATH = os.getcwd()
CHROMA_PATH = os.path.join(CUR_PATH, "data/chroma_db")
DATA_PATH = os.path.join(CUR_PATH, "data/chunks")

def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new DB from the documents.
    Chroma.from_documents(
        chunks, OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434"), persist_directory=CHROMA_PATH
    )
    
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")

def load_chunks() -> list[Document]:
    chunks = []
    for filename in os.listdir(DATA_PATH):
        if filename.endswith(".txt"):
            file_path = os.path.join(DATA_PATH, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                chunk = Document(page_content=content, metadata={"source": filename})
                chunks.append(chunk)
    print(f"Loaded {len(chunks)} chunks from {DATA_PATH}.")
    return chunks

def main():
    chunks = Util.time_execution(load_chunks) # ~11.85s to load all chunks
    Util.time_execution(lambda: save_to_chroma(chunks)) # 1000 chunks ~ 16.5s, all chunks ~ 45 min

if __name__ == "__main__":
    main()