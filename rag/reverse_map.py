import os, sys
import json
from langchain_core.documents import Document
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from open_config import load_config
config = load_config()
MAPPING_PATH = os.path.join(config["cwd"], config["mappings_path"])
if (not os.path.exists(MAPPING_PATH)):
    raise FileNotFoundError(f"Mappings path {MAPPING_PATH} does not exist.")
CHUNK_MAPPING_FILE = os.path.join(MAPPING_PATH, config["chunk_mapping_file"])
DOC_MAPPING_FILE = os.path.join(MAPPING_PATH, config["doc_mapping_file"])

chunk_mappings = json.load(open(CHUNK_MAPPING_FILE, "r", encoding="utf-8"))
doc_mappings = json.load(open(DOC_MAPPING_FILE, "r", encoding="utf-8"))

cwd = config["cwd"]

def get_url_from_chunk(chunk: Document) -> str:
    chunk_id = chunk.metadata.get("source", None)
    if chunk_id is None:
        print("Chunk is missing source metadata.")
        return ""
    doc_id = chunk_mappings.get(os.path.join(cwd, chunk_id), None)
    if doc_id is None:
        print("Document ID not found for chunk.")
        return ""
    url = doc_mappings.get(doc_id, None)
    return url