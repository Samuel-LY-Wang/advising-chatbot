import json
import os
from pathlib import Path
CUR_PATH = Path.cwd()

def load_chunk_doc_mapping(mapping_path):
    try:
        return json.load(open(mapping_path, "r", encoding="utf-8"))
    except FileNotFoundError:
        print(f"Mapping file not found: {mapping_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {mapping_path}")
        return {}

mapping = load_chunk_doc_mapping(os.path.join(CUR_PATH, "data/chunks/doc_chunk_mapping.json"))

def get_source_url(source_filename, mapping):
    # mapping is now complete index
    return mapping.get(str(source_filename), None)